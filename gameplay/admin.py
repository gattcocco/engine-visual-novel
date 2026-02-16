from django.contrib import admin
from .models import Scena, DialogLine, Scelta

# Questo permette di scrivere le battute DENTRO la pagina della Scena
class DialogLineInline(admin.TabularInline):
    model = DialogLine
    extra = 1 # Quante righe vuote mostrare di default

# Questo permette di aggiungere le Scelte DENTRO la pagina della Scena
class SceltaInline(admin.TabularInline):
    model = Scelta
    fk_name = 'scena_partenza'
    extra = 1

@admin.register(Scena)
class ScenaAdmin(admin.ModelAdmin):
    inlines = [DialogLineInline, SceltaInline]

# Non serve registrare DialogLine e Scelta separatamente se usiamo gli inline,
# ma a volte è comodo averli. Per ora registriamo solo la Scena "Master".