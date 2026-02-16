from django.contrib import admin
from django.urls import path
from django.conf import settings # <--- NUOVO
from django.conf.urls.static import static # <--- NUOVO
from gameplay.views import motore_gioco

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', motore_gioco, name='home'),
    path('<slug:slug_scena>/', motore_gioco, name='scena'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # <--- NUOVO