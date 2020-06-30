from django.contrib.postgres.fields import ArrayField
from django.db import models

class ObstSorten(models.Model):
    obst_type       = models.TextChoices('Obst_Type', 'Apfel, Birne, Kirche, Zwetschge, Nuss, Quitte, Mispel, unbekannt')
    obst_sorte      = models.CharField(max_length=64,
        help_text='Obstsorte: Name der Obstsorte. z.B. rheinischer Winterrambour')
    pflueck_reif    = models.CharField(max_length=30, blank=True)
    genuss_reif     = models.CharField(max_length=30, blank=True)
    verwendung      = models.CharField(max_length=248)
    geschmack       = models.CharField(max_length=248)
    lagerfaehigkeit = models.CharField(max_length=248)
    alergie_info    = models.CharField(max_length=248)
    www             = ArrayField(models.URLField(max_length=128, blank=True),
                                 size=5)
    bilder          = ArrayField(models.ImageField(upload_to='uploads/Sorte'),
                                 blank=True, size=20)

class Wiese(models.Model):
    wiesen_id     = models.AutoField(primary_key=True)
    name          = models.CharField(max_length=30)
    bilder        = ArrayField(models.ImageField(upload_to='uploads/Wiese'),
                                 blank=True, size=20)
    grafik        = models.ImageField(upload_to='uploads/Wiese', default=None)
    obstwiese     = models.BooleanField(default=True)
    bluehwiese    = models.BooleanField(default=False)

class ObstBaum(models.Model):
    baum_id     = models.AutoField(primary_key=True)
    obst_sorte  = models.ForeignKey(ObstSorten, on_delete=models.CASCADE)
    wiese       = models.ForeignKey(Wiese, on_delete=models.CASCADE)
    bilder      = ArrayField(models.ImageField(upload_to='uploads/Wiese'),
                                 blank=True, size=20)
    zustand     = models.CharField(max_length=248, blank=True)
    letzter_schnitt = models.DateField(null=True)
    

