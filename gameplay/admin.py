from django.contrib import admin
from .models import Scena, DialogLine, Scelta, Oggetto, ActionNode

admin.site.register(Oggetto)

class DialogLineInline(admin.TabularInline):
    model = DialogLine
    extra = 1

class SceltaInline(admin.TabularInline):
    model = Scelta
    fk_name = 'scena_partenza'
    extra = 1

# NUOVO INLINE
class ActionNodeInline(admin.TabularInline):
    model = ActionNode
    fk_name = 'scena_partenza'
    extra = 1

@admin.register(Scena)
class ScenaAdmin(admin.ModelAdmin):
    # Aggiunto ActionNodeInline alla lista
    inlines = [DialogLineInline, SceltaInline, ActionNodeInline]
    list_display = ['titolo', 'slug']