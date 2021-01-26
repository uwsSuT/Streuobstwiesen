from django.contrib.postgres.fields import ArrayField
from django.db import models

class Hofladen(models.Model):
    id       = models.IntegerField(primary_key=True)
    name     = models.CharField(max_length=64,
                       help_text='Name des Ladens oder Ansprechpartners',)
    adresse  = models.CharField(max_length=128)
    plz      = models.CharField(max_length=8, blank=True, null=True)
    ort      = models.CharField(max_length=128)
    tel_nr   = models.CharField(max_length=32)
    www      = models.CharField(max_length=256)
    email    = models.CharField(max_length=128, blank=True, null=True)
    vertrieb = models.CharField(max_length=1024)
    int_www  = models.CharField(max_length=256, blank=True, null=True)
    # Liste von Möglichkeiten: Imker, Hofladen, Metzger, ...
    kategorie = models.CharField(max_length=1024, blank=True, null=True)
    # Rubriken beinhaltet die Waren die der Hofladen anbietet
    # Die Werte werden durch eine 0 | 1 definiert, das textuelle Gegenstück
    # wird in einer Python Datei definiert (hofladen/rubriken)
    # X, Y Koordinate als String muss im Prog. umgewandelt werden
    coordinate = models.CharField(max_length=24, blank=True, null=True)

    def __str__(self):
        return self.name

