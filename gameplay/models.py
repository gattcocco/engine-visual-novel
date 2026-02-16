from django.db import models


# 1. NUOVO MODELLO: L'OGGETTO
class Oggetto(models.Model):
    nome = models.CharField(max_length=100)
    icona = models.ImageField(upload_to='oggetti/', blank=True, null=True) # L'immagine nello zaino

    # AGGIUNGI QUESTO PEZZO QUI SOTTO:
    class Meta:
        verbose_name = "Oggetto"
        verbose_name_plural = "Oggetti"

    def __str__(self):
        return self.nome


class Scena(models.Model):
    slug = models.SlugField(primary_key=True)
    titolo = models.CharField(max_length=200)
    # Sfondo della scena (es. "aula_scolastica.jpg")
    background = models.ImageField(upload_to='backgrounds/', blank=True, null=True)

    # AGGIUNGI QUESTO PEZZO QUI SOTTO:
    class Meta:
        verbose_name = "Scena"
        verbose_name_plural = "Scene"

    def __str__(self):
        return self.titolo

class DialogLine(models.Model):
    # Collegamento alla scena madre
    scena = models.ForeignKey(Scena, related_name='dialogues', on_delete=models.CASCADE)
    
    # Ordine della battuta (1, 2, 3...)
    order = models.PositiveIntegerField()
    
    # Chi parla?
    character_name = models.CharField(max_length=100)
    
    # Espressione/Sprite (es. "faccia_arrabbiata.png" o un codice testo)
    # Uso ImageField per caricare il file vero e proprio
    character_sprite = models.ImageField(upload_to='sprites/', blank=True, null=True)
    
    # Cosa dice?
    text = models.TextField()

    class Meta:
        ordering = ['order'] # Ordina sempre per numero progressivo

    def __str__(self):
        return f"{self.order}. {self.character_name}: {self.text[:30]}..."

# 2. AGGIORNAMENTO SCELTA: ORA HA CONSEGUENZE
class Scelta(models.Model):
    scena_partenza = models.ForeignKey(Scena, related_name='scelte', on_delete=models.CASCADE)
    testo_bottone = models.CharField(max_length=200)
    scena_arrivo = models.ForeignKey(Scena, related_name='scelte_in_arrivo', on_delete=models.SET_NULL, null=True, blank=True)
    
    # NOVITÀ: Logica RPG
    oggetto_ricevuto = models.ForeignKey(Oggetto, related_name='scelte_che_danno', on_delete=models.SET_NULL, blank=True, null=True)
    oggetto_richiesto = models.ForeignKey(Oggetto, related_name='scelte_che_richiedono', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.testo_bottone} (Richiede: {self.oggetto_richiesto} -> Dà: {self.oggetto_ricevuto})"