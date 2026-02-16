from django.db import models

class Oggetto(models.Model):
    nome = models.CharField(max_length=100)
    icona = models.ImageField(upload_to='oggetti/', blank=True, null=True)

    class Meta:
        verbose_name = "Oggetto"
        verbose_name_plural = "Oggetti"

    def __str__(self):
        return self.nome

class Scena(models.Model):
    slug = models.SlugField(primary_key=True)
    titolo = models.CharField(max_length=200)
    background = models.ImageField(upload_to='backgrounds/', blank=True, null=True)

    class Meta:
        verbose_name = "Scena"
        verbose_name_plural = "Scene"

    def __str__(self):
        return self.titolo

class DialogLine(models.Model):
    scena = models.ForeignKey(Scena, related_name='dialogues', on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    character_name = models.CharField(max_length=100)
    character_sprite = models.ImageField(upload_to='sprites/', blank=True, null=True)
    text = models.TextField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.character_name}: {self.text[:30]}..."

class Scelta(models.Model):
    scena_partenza = models.ForeignKey(Scena, related_name='scelte', on_delete=models.CASCADE)
    testo_bottone = models.CharField(max_length=200)
    scena_arrivo = models.ForeignKey(Scena, related_name='scelte_in_arrivo', on_delete=models.SET_NULL, null=True, blank=True)
    oggetto_ricevuto = models.ForeignKey(Oggetto, related_name='scelte_che_danno', on_delete=models.SET_NULL, blank=True, null=True)
    oggetto_richiesto = models.ForeignKey(Oggetto, related_name='scelte_che_richiedono', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = "Scelta"
        verbose_name_plural = "Scelte"

    def __str__(self):
        return f"{self.testo_bottone}"

# --- NUOVO MODELLO ACTION NODE ---
class ActionNode(models.Model):
    scena_partenza = models.ForeignKey(Scena, related_name='action_nodes', on_delete=models.CASCADE)
    testo_bottone = models.CharField(max_length=200) # Es. "Esamina la porta", "Usa oggetto su..."
    
    # Logica: Se clicco questo bottone, entro in "modalità selezione oggetto"
    # Se seleziono l'oggetto giusto (oggetto_richiesto) -> vado a scena_successo
    # Se seleziono l'oggetto sbagliato -> vado a scena_fallimento (opzionale)
    
    oggetto_richiesto = models.ForeignKey(Oggetto, related_name='action_nodes_che_richiedono', on_delete=models.SET_NULL, null=True, blank=True)
    scena_successo = models.ForeignKey(Scena, related_name='action_nodes_successo', on_delete=models.SET_NULL, null=True, blank=True)
    scena_fallimento = models.ForeignKey(Scena, related_name='action_nodes_fallimento', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Action Node"
        verbose_name_plural = "Action Nodes"

    def __str__(self):
        return self.testo_bottone