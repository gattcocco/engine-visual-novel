from django.shortcuts import render, get_object_or_404, redirect
from .models import Scena, Scelta, Oggetto, ActionNode

def fai_scelta(request, scelta_id):
    scelta = get_object_or_404(Scelta, id=scelta_id)
    
    if 'inventario' not in request.session:
        request.session['inventario'] = []

    if scelta.oggetto_ricevuto:
        id_oggetto = scelta.oggetto_ricevuto.id
        if id_oggetto not in request.session['inventario']:
            request.session['inventario'].append(id_oggetto)
            request.session.modified = True

    if scelta.scena_arrivo:
        return redirect('scena', slug_scena=scelta.scena_arrivo.slug)
    else:
        return redirect('home')

# --- NUOVE FUNZIONI ACTION NODE ---

def avvia_action_node(request, action_node_id):
    # L'utente ha cliccato su un bottone tipo "Usa un oggetto su questa porta"
    action_node = get_object_or_404(ActionNode, id=action_node_id)
    # Salviamo in sessione che siamo in "modalità scelta oggetto" per questo nodo
    request.session['action_node_attivo_id'] = action_node.id
    request.session.modified = True
    return redirect('scena', slug_scena=action_node.scena_partenza.slug)

def applica_oggetto_action_node(request, action_node_id, oggetto_id):
    # L'utente ha cliccato un oggetto dell'inventario MENTRE era attivo un ActionNode
    action_node = get_object_or_404(ActionNode, id=action_node_id)
    inventario_ids = request.session.get('inventario', [])

    # Sicurezza: l'utente possiede davvero l'oggetto?
    if oggetto_id not in inventario_ids:
        request.session['action_node_attivo_id'] = None
        request.session.modified = True
        return redirect('scena', slug_scena=action_node.scena_partenza.slug)

    # CHECK: È l'oggetto giusto?
    if action_node.oggetto_richiesto and action_node.oggetto_richiesto.id == oggetto_id:
        # SUCCESSO!
        request.session['action_node_attivo_id'] = None # Resetta stato
        request.session.modified = True
        if action_node.scena_successo:
            return redirect('scena', slug_scena=action_node.scena_successo.slug)
    
    # FALLIMENTO (Oggetto sbagliato)
    request.session['action_node_attivo_id'] = None # Resetta stato
    request.session.modified = True
    if action_node.scena_fallimento:
        return redirect('scena', slug_scena=action_node.scena_fallimento.slug)
    
    # Se non c'è scena fallimento, ricarica semplicemente la scena corrente
    return redirect('scena', slug_scena=action_node.scena_partenza.slug)


def motore_gioco(request, slug_scena='inizio'):
    scena = get_object_or_404(Scena, slug=slug_scena)
    
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

    inventario_ids = request.session.get('inventario', [])
    
    # Filtro Scelte Classiche
    tutte_scelte = scena.scelte.all()
    scelte_visibili = []
    for s in tutte_scelte:
        if s.oggetto_richiesto:
            if s.oggetto_richiesto.id in inventario_ids:
                scelte_visibili.append(s)
        else:
            scelte_visibili.append(s)
            
    # Recupera Action Nodes
    action_nodes = scena.action_nodes.all()

    # Controlla se siamo in modalità "Selezione Oggetto"
    action_node_attivo = None
    action_node_attivo_id = request.session.get('action_node_attivo_id')
    if action_node_attivo_id:
        # Verifica che il nodo attivo appartenga davvero a questa scena (per sicurezza)
        action_node_attivo = ActionNode.objects.filter(id=action_node_attivo_id, scena_partenza=scena).first()
        # Se l'utente ha cambiato scena, resettiamo l'azione
        if not action_node_attivo:
             request.session['action_node_attivo_id'] = None

    oggetti_inventario = Oggetto.objects.filter(id__in=inventario_ids)

    return render(request, 'gameplay/schermata.html', {
        'scena': scena,
        'battuta': battuta_attuale,
        'mostra_scelte': mostra_scelte,
        'prossimo_step': prossimo_step,
        'scelte': scelte_visibili,
        'inventario': oggetti_inventario,
        'action_nodes': action_nodes,         # Passiamo i nodi al template
        'action_node_attivo': action_node_attivo, # Passiamo lo stato attivo
    })
# ... (dopo le altre funzioni)

def reset_gioco(request):
    request.session.flush() # CANCELLA TUTTO: Inventario, variabili, tutto.
    return redirect('home')