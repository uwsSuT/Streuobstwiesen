from django.db import models
from django.contrib.postgres.fields import ArrayField

class Entwicklungsziele(models.Model):
    id            = models.IntegerField(primary_key=True)
    ziel          = models.CharField(max_length=256, blank=True, null=True)

class PflegeMassnahme(models.Model):
    id            = models.IntegerField(primary_key=True)
    datum         = models.DateTimeField(null=True, blank=True)
    wer           = models.CharField(max_length=64, blank=True, null=True)
    bezeichnung   = models.CharField(max_length=2048, blank=True, null=True)
    erledigt      = models.BooleanField(default=False)

class Baumarten(models.Model):
    name          = models.CharField(max_length=64, blank=True, null=True)
    www           = ArrayField(models.URLField(max_length=256, blank=True),
                                 size=5, null=True)

class Blumen(models.Model):
    name          = models.CharField(max_length=64, blank=True, null=True)
    www           = ArrayField(models.URLField(max_length=256, blank=True),
                                 size=5, null=True)

class Graeser(models.Model):
    name          = models.CharField(max_length=64, blank=True, null=True)
    www           = ArrayField(models.URLField(max_length=256, blank=True),
                                 size=5, null=True)

class Kraeuter(models.Model):
    name          = models.CharField(max_length=64, blank=True, null=True)
    www           = ArrayField(models.URLField(max_length=256, blank=True),
                                 size=5, null=True)

class Wiese(models.Model):
    wiesen_id     = models.IntegerField(primary_key=True)
    name          = models.CharField(max_length=64)
    obstwiese     = models.BooleanField(default=True)
    bluehwiese    = models.BooleanField(default=False)
    www_name      = models.CharField(max_length=128, blank=True, null=True)

    #
    # Flur Daten
    #
    biotop_nr     = models.IntegerField(blank=True, null=True)
    flur_nr       = models.IntegerField(blank=True, null=True)
    groesse       = models.IntegerField(blank=True, null=True)
    eigentuemer   = models.CharField(max_length=64, blank=True, null=True)
    lage          = models.CharField(max_length=256, blank=True, null=True)

    #
    # Bestandsdaten
    #
    standort      = models.CharField(max_length=256, blank=True, null=True)
    ogestalt      = models.CharField(max_length=256, blank=True, null=True)
    angr_nutzung  = models.CharField(max_length=256, blank=True, null=True)
    beschreibung  = models.CharField(max_length=256, blank=True, null=True)
    bes_planzen_tiere = models.CharField(max_length=256, blank=True, null=True)

    #
    # Entwicklungsziele
    #
    ziel_beschreibung  = models.ManyToManyField(Entwicklungsziele,
                                     related_name='wiese_ziele')

    #
    # Massnahmen
    #
    sicherungs_massnahmen  = models.CharField(max_length=256, blank=True, null=True)
    pflege_massnahmen_plan = models.ManyToManyField(PflegeMassnahme,
                                     related_name='plan_massnahme')

    pflege_massnahmen_ist = models.ManyToManyField(PflegeMassnahme,
                                     related_name='ist_massnahme')

    #
    # sonstiges
    #
    pate  = models.CharField(max_length=64, blank=True, null=True)
    zufahrt  = models.BooleanField(default=True)
    foerderung_moeglich = models.BooleanField(default=False)
    foerderung_beantragt = models.BooleanField(default=False)
    gepflegt_durch = models.CharField(max_length=64, blank=True, null=True)


    anmerkungen = models.CharField(max_length=1024, blank=True, null=True)
    letzte_pflege = models.DateTimeField(null=True, blank=True)

    #
    # Bewuchs
    #
    baeume = models.ManyToManyField(Baumarten, related_name='wiese_baum')
    blumen = models.ManyToManyField(Blumen, related_name='wiese_blume')
    graeser = models.ManyToManyField(Graeser, related_name='wiese_gras')
    kraeuter = models.ManyToManyField(Kraeuter, related_name='wiese_kraut')

    def __str__(self):
        return self.www_name

