from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# IMPORTANTE: Aggiungi 'reset_gioco' alla fine della lista degli import!
from gameplay.views import motore_gioco, fai_scelta, avvia_action_node, applica_oggetto_action_node, applica_target, reset_gioco 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- IL PEZZO MANCANTE ---
    path('reset/', reset_gioco, name='reset_gioco'), 
    # -------------------------

    path('azione/<int:scelta_id>/', fai_scelta, name='fai_scelta'),
    path('action-node/<int:action_node_id>/start/', avvia_action_node, name='avvia_action_node'),
    path('action-node/<int:action_node_id>/apply/<int:oggetto_id>/', applica_oggetto_action_node, name='applica_oggetto_action_node'), 
    path('<slug:slug_scena>/target/<slug:target_slug>/', applica_target, name='applica_target'),

    path('', motore_gioco, name='home'),
    path('<slug:slug_scena>/', motore_gioco, name='scena'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)