from django.shortcuts import render, get_object_or_404, redirect
from .models import Scena, Scelta, Oggetto, ActionNode

def fai_scelta(request, scelta_id):
    scelta = get_object_or_404(Scelta, id=scelta_id)
    
    if 'inventario' not in request.session:
        request.session['inventario'] = []

    if scelta.oggetto_richiesto and scelta.oggetto_richiesto.id not in request.session['inventario']:
        request.session['feedback_message'] = "Non hai l'oggetto richiesto."
        request.session.modified = True
        return redirect('scena', slug_scena=scelta.scena_partenza.slug)

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
    request.session['last_action_node_id'] = action_node.id
    request.session['selected_item_id'] = None
    request.session.modified = True
    return redirect('scena', slug_scena=action_node.scena_partenza.slug)

def applica_oggetto_action_node(request, action_node_id, oggetto_id):
    # L'utente ha cliccato un oggetto dell'inventario MENTRE era attivo un ActionNode
    action_node = get_object_or_404(ActionNode, id=action_node_id)
    inventario_ids = request.session.get('inventario', [])

    # Sicurezza: l'utente possiede davvero l'oggetto?
    if oggetto_id not in inventario_ids:
        request.session['action_node_attivo_id'] = None
        request.session['selected_item_id'] = None
        request.session['feedback_message'] = "Oggetto non disponibile nello zaino."
        request.session.modified = True
        return redirect('scena', slug_scena=action_node.scena_partenza.slug)

    request.session['selected_item_id'] = oggetto_id
    request.session['action_node_attivo_id'] = None
    request.session['feedback_message'] = 'Ora scegli un target.'
    request.session.modified = True
    return redirect('scena', slug_scena=action_node.scena_partenza.slug)


def applica_target(request, slug_scena, target_slug):
    scena = get_object_or_404(Scena, slug=slug_scena)
    verb_mode = request.session.get('verb_mode')

    if not verb_mode:
        request.session['feedback_message'] = 'Seleziona un comando.'
        request.session.modified = True
        return redirect('scena', slug_scena=scena.slug)

    selected_item_id = request.session.get('selected_item_id')
    last_action_node_id = request.session.get('last_action_node_id')

    if not selected_item_id or not last_action_node_id:
        request.session['feedback_message'] = 'Prima seleziona un oggetto.'
        request.session['selected_item_id'] = None
        request.session['last_action_node_id'] = None
        request.session['action_node_attivo_id'] = None
        request.session.modified = True
        return redirect('scena', slug_scena=scena.slug)

    action_node = ActionNode.objects.filter(id=last_action_node_id, scena_partenza=scena).first()
    if not action_node:
        request.session['feedback_message'] = 'Azione non valida in questa scena.'
        request.session['selected_item_id'] = None
        request.session['last_action_node_id'] = None
        request.session['action_node_attivo_id'] = None
        request.session.modified = True
        return redirect('scena', slug_scena=scena.slug)

    if target_slug != 'porta':
        request.session['feedback_message'] = 'Target non valido.'
        request.session['selected_item_id'] = None
        request.session['last_action_node_id'] = None
        request.session['action_node_attivo_id'] = None
        request.session.modified = True
        if action_node.scena_fallimento:
            return redirect('scena', slug_scena=action_node.scena_fallimento.slug)
        return redirect('scena', slug_scena=scena.slug)

    inventario_ids = request.session.get('inventario', [])
    if selected_item_id not in inventario_ids:
        request.session['feedback_message'] = 'Oggetto non disponibile nello zaino.'
        request.session['selected_item_id'] = None
        request.session['last_action_node_id'] = None
        request.session['action_node_attivo_id'] = None
        request.session.modified = True
        return redirect('scena', slug_scena=scena.slug)

    if action_node.oggetto_richiesto and action_node.oggetto_richiesto.id == selected_item_id:
        request.session['inventario'] = [obj_id for obj_id in inventario_ids if obj_id != selected_item_id]
        request.session['feedback_message'] = 'Hai usato correttamente l\'oggetto sulla porta.'
        request.session['selected_item_id'] = None
        request.session['last_action_node_id'] = None
        request.session['action_node_attivo_id'] = None
        request.session.modified = True
        if action_node.scena_successo:
            return redirect('scena', slug_scena=action_node.scena_successo.slug)
        return redirect('scena', slug_scena=scena.slug)

    request.session['feedback_message'] = 'Non sembra funzionare su quel target.'
    request.session['selected_item_id'] = None
    request.session['last_action_node_id'] = None
    request.session['action_node_attivo_id'] = None
    request.session.modified = True
    if action_node.scena_fallimento:
        return redirect('scena', slug_scena=action_node.scena_fallimento.slug)
    return redirect('scena', slug_scena=scena.slug)


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
    feedback_message = request.session.pop('feedback_message', None)
    
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
    selected_item_id = request.session.get('selected_item_id')
    verb_mode = request.session.get('verb_mode')
    if action_node_attivo_id:
        # Verifica che il nodo attivo appartenga davvero a questa scena (per sicurezza)
        action_node_attivo = ActionNode.objects.filter(id=action_node_attivo_id, scena_partenza=scena).first()
        # Se l'utente ha cambiato scena, resettiamo l'azione
        if not action_node_attivo:
             request.session['action_node_attivo_id'] = None
             request.session.modified = True

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
        'verb_mode': verb_mode,
        'selected_item_id': selected_item_id,
        'feedback': feedback_message,
    })


def set_verb_mode(request, slug_scena, verb):
    request.session['verb_mode'] = verb
    if verb != 'usa':
        request.session['selected_item_id'] = None
    request.session.modified = True
    return redirect('scena', slug_scena=slug_scena)


def annulla_comando(request, slug_scena):
    request.session['verb_mode'] = None
    request.session['selected_item_id'] = None
    request.session['last_action_node_id'] = None
    request.session['action_node_attivo_id'] = None
    request.session.modified = True
    return redirect('scena', slug_scena=slug_scena)
# ... (dopo le altre funzioni)

def reset_gioco(request):
    request.session.flush() # CANCELLA TUTTO: Inventario, variabili, tutto.
    return redirect('home')
