from django.shortcuts import render, get_object_or_404, redirect
from .models import Scena, Scelta, Oggetto

# Questa vista gestisce il click sulla scelta (LOGICA)
def fai_scelta(request, scelta_id):
    scelta = get_object_or_404(Scelta, id=scelta_id)
    
    # 1. Inizializza l'inventario se non esiste
    if 'inventario' not in request.session:
        request.session['inventario'] = []

    # 2. Se la scelta dà un oggetto, aggiungilo allo zaino
    if scelta.oggetto_ricevuto:
        id_oggetto = scelta.oggetto_ricevuto.id
        if id_oggetto not in request.session['inventario']:
            request.session['inventario'].append(id_oggetto)
            request.session.modified = True # Importante! Dice a Django di salvare

    # 3. Vai alla scena successiva
    if scelta.scena_arrivo:
        return redirect('scena', slug_scena=scelta.scena_arrivo.slug)
    else:
        return redirect('home') # Fallback se non c'è destinazione

# Questa vista mostra la scena (VISUALIZZAZIONE)
def motore_gioco(request, slug_scena='inizio'):
    scena = get_object_or_404(Scena, slug=slug_scena)
    
    # Recupera le battute
    battute = scena.dialogues.all().order_by('order')
    totale_battute = battute.count()
    
    try:
        step_corrente = int(request.GET.get('step', 1))
    except ValueError:
        step_corrente = 1

    battuta_attuale = None
    mostra_scelte = False
    prossimo_step = None

    if step_corrente <= totale_battute:
        battuta_attuale = battute[step_corrente - 1]
        prossimo_step = step_corrente + 1
    else:
        mostra_scelte = True

    # --- LOGICA FILTRO SCELTE ---
    # Recuperiamo l'inventario attuale
    inventario_ids = request.session.get('inventario', [])
    
    # Prendiamo tutte le scelte possibili
    tutte_scelte = scena.scelte.all()
    scelte_visibili = []

    for s in tutte_scelte:
        # Se la scelta richiede un oggetto...
        if s.oggetto_richiesto:
            # ...e l'utente CE L'HA -> Mostra
            if s.oggetto_richiesto.id in inventario_ids:
                scelte_visibili.append(s)
            # ...e l'utente NON CE L'HA -> Nascondi (non la aggiungo alla lista)
        else:
            # Se non richiede nulla -> Mostra sempre
            scelte_visibili.append(s)
            
    # Recuperiamo gli oggetti veri per disegnarli a schermo (HUD)
    oggetti_inventario = Oggetto.objects.filter(id__in=inventario_ids)

    return render(request, 'gameplay/schermata.html', {
        'scena': scena,
        'battuta': battuta_attuale,
        'mostra_scelte': mostra_scelte,
        'prossimo_step': prossimo_step,
        'scelte': scelte_visibili, # Passo solo quelle filtrate!
        'inventario': oggetti_inventario # Passo lo zaino al template
    })