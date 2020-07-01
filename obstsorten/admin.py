from django.contrib import admin

from .models import ObstSorten, Wiese, ObstBaum

admin.site.register(ObstSorten)
admin.site.register(Wiese)
admin.site.register(ObstBaum)
