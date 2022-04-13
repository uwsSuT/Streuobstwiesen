from django.contrib.postgres.fields import ArrayField
from django.db import models

class ObstTypen(models.Model):
    id  = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, blank=False)

class ObstSorten(models.Model):
    sorten_id       = models.IntegerField(primary_key=True)
    obst_type       = models.IntegerField()
    type_name       = models.ForeignKey(ObstTypen, on_delete=models.CASCADE)
    obst_sorte      = models.CharField(max_length=64,
        help_text='Obstsorte: Name der Obstsorte. z.B. rheinischer Winterrambour', null=True)
    pflueck_reif    = models.CharField(max_length=1024, blank=True, null=True)
    genuss_reif     = models.CharField(max_length=1024, blank=True, null=True)
    verwendung      = models.CharField(max_length=1024, null=True)
    geschmack       = models.CharField(max_length=1024, null=True)
    lagerfaehigkeit = models.CharField(max_length=1024, null=True)
    alergie_info    = models.CharField(max_length=1024, null=True)
    www             = ArrayField(models.URLField(max_length=256, blank=True),
                                 size=5, null=True)

    def __str__(self):
        return self.obst_sorte

class Wiese(models.Model):
    wiesen_id     = models.IntegerField(primary_key=True)
    name          = models.CharField(max_length=64)
    obstwiese     = models.BooleanField(default=True)
    bluehwiese    = models.BooleanField(default=False)
    www_name      = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.www_name

class ObstBaum(models.Model):
    baum_id     = models.AutoField(primary_key=True)
    sorten_id   = models.ForeignKey(ObstSorten, on_delete=models.CASCADE)
    wiese       = models.ForeignKey(Wiese, on_delete=models.CASCADE)
    zustand     = models.CharField(max_length=248, blank=True)
    letzter_schnitt = models.DateField(null=True, blank=True)
    letzte_duengung = models.DateField(null=True, blank=True)
    duengung_noetig = models.BooleanField(default=False)
    coordinate = models.CharField(max_length=24, blank=True, null=True)

    def __str__(self):
        try:
            return "%s_%s" % (self.baum_id, self.sorten_id.obst_sorte)
        except:
            return "%s" % self.baum_id


