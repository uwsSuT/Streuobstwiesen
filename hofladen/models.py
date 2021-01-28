from django.contrib.postgres.fields import ArrayField
from django.db import models

class Hofladen(models.Model):
    """
        Alle Attribute eines Hofladens mit einer Liste der Angebotenen Artikel (Rubriken)
    """
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
    kategorie = ArrayField(models.IntegerField(), size=32, blank=True, null=True)
    # Rubriken beinhaltet die Waren die der Hofladen anbietet
    # Die Werte werden durch eine 0 | 1 definiert, das textuelle Gegenstück
    # wird in einer Python Datei definiert (hofladen/rubriken)
    # X, Y Koordinate als String muss im Prog. umgewandelt werden
    coordinate = models.CharField(max_length=24, blank=True, null=True)

    def __str__(self):
        return self.name

class Unterrubrik(models.Model):
    """
        Liste der Artikel in einer Rubrik
        z.B. Honig und Propolis in der Rubrik "Bienenprodukte"
    """
    id       = models.AutoField(primary_key=True)
    name     = models.CharField(max_length=64,
                       help_text='Name der Artikels',)
    hofladen_list = ArrayField(models.IntegerField(), size=1024, blank=True, null=True)
    rubrik   = models.ForeignKey('HofRubrik', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class HofRubrik(models.Model):
    """
        List der von uns berücksichtigten Artikel und Kategorien
    """
    id       = models.AutoField(primary_key=True)
    name     = models.CharField(max_length=64,
                       help_text='Name der Rubrik',)
    hofladen_list = ArrayField(models.IntegerField(), size=1024, blank=True, null=True)
    unter_rubriken = ArrayField(models.IntegerField(), size=1024, blank=True, null=True)

    def __str__(self):
        return self.name
        
