from django.contrib import admin

from .models import ObstSorten, ObstBaum
from wiese.models import Wiese
from hofladen.models import Hofladen, Unterrubrik, HofRubrik

admin.site.register(ObstSorten)
admin.site.register(Wiese)
admin.site.register(ObstBaum)
admin.site.register(Hofladen)
admin.site.register(HofRubrik)
admin.site.register(Unterrubrik)
