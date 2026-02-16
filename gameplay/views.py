from django.shortcuts import render, get_object_or_404
from .models import Scena

def motore_gioco(request, slug_scena='inizio'):
    # 1. Trova la scena corrente
    scena = get_object_or_404(Scena, slug=slug_scena)
    
    # 2. Carica tutte le battute di questa scena, ordinate
    battute = scena.dialogues.all().order_by('order')
    totale_battute = battute.count()
    
    # 3. Capiamo a che "step" siamo (leggendolo dall'URL, default = 1)
    try:
        step_corrente = int(request.GET.get('step', 1))
    except ValueError:
        step_corrente = 1

    # 4. Logica: Mostro la battuta o le scelte?
    battuta_attuale = None
    mostra_scelte = False
    prossimo_step = None

    if step_corrente <= totale_battute:
        # Siamo ancora nel dialogo (nota: le liste partono da 0, quindi step-1)
        battuta_attuale = battute[step_corrente - 1]
        prossimo_step = step_corrente + 1
    else:
        # Dialogo finito, tocca al giocatore scegliere
        mostra_scelte = True

    # 5. Impacchetta tutto e spedisci al template
    return render(request, 'gameplay/schermata.html', {
        'scena': scena,
        'battuta': battuta_attuale,
        'mostra_scelte': mostra_scelte,
        'prossimo_step': prossimo_step,
        'scelte': scena.scelte.all()
    })