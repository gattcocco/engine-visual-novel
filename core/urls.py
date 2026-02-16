from django.contrib import admin
from django.urls import path
from django.conf import settings # <--- NUOVO
from django.conf.urls.static import static # <--- NUOVO
from gameplay.views import motore_gioco, fai_scelta # <--- Importa anche fai_scelta!

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URL PER L'AZIONE (Invisibile all'utente, serve solo per la logica)
    path('azione/<int:scelta_id>/', fai_scelta, name='fai_scelta'), 

    path('', motore_gioco, name='home'),
    path('<slug:slug_scena>/', motore_gioco, name='scena'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)