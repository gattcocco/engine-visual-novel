from django.contrib import admin
# 1. IMPORTIAMO TUTTI I MODELLI (Compreso Oggetto!)
from .models import Scena, DialogLine, Scelta, Oggetto 

# 2. REGISTRAZIONE SEMPLICE
# Questo crea il pannello per creare/modificare gli oggetti (Chiavi, Spade, ecc.)
admin.site.register(Oggetto)

# --- CONFIGURAZIONI AVANZATE PER LE SCENE (Già le avevi) ---

class DialogLineInline(admin.TabularInline):
    model = DialogLine
    extra = 1

class SceltaInline(admin.TabularInline):
    model = Scelta
    fk_name = 'scena_partenza'
    extra = 1

@admin.register(Scena)
class ScenaAdmin(admin.ModelAdmin):
    inlines = [DialogLineInline, SceltaInline]
    # Opzionale: mostra queste colonne nell'elenco delle scene
    list_display = ['titolo', 'slug']