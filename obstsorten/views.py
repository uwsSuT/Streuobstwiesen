import os
from os.path import join
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView
from obstsorten.models import Wiese, ObstBaum, ObstSorten, Obst_Type

APP = 'obstsorten'

class HomePageView(TemplateView):
    template_name = 'home.html'


class AboutPageView(TemplateView):
    template_name = 'about.html'

    def get(self, request, *args, **kwargs):
        from hilgi import Version
        context = { 'VERSION' : Version }
        return render(request, self.template_name, context)

class ObstSortenView(TemplateView):
    template_name = 'obstsorten.html'

    def __find_grafik__(self, oid):
        """
            such die zur Obstsorte zugehörige Grafik in dem Static Verzeichnis
        """
        pwd = os.getcwd()
        for f in os.listdir(join(pwd, 'static', 'images', APP)):
            if f.find("%s_" % oid) == 0:
                #print("OBST-BILD gefunden %s" % f)
                return join('images', APP, f)

    def get_queryset(self):
        obst = ObstSorten.objects.all().order_by('sorten_id')
        robst = []
        for o in obst:
            sorte = {
                'obst_type' : Obst_Type[o.obst_type],
                'obst_sorte' : o.obst_sorte,
                'pflueck_reif' : o.pflueck_reif,
                'verwendung' : o.verwendung,
                'geschmack' : o.geschmack,
                'lagerfaehigkeit' : o.lagerfaehigkeit,
                'alergie_info' : o.alergie_info,
                'www' : o.www,
                'picture' : self.__find_grafik__(o.sorten_id),
                }
            robst.append(sorte)
        return robst

    def get(self, request, sid=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_queryset(),
                   'wiesen_list' : Wiese.objects.all().order_by('wiesen_id'),
                   'obstsorten_list' : ObstSorten.objects.all().order_by('sorten_id'),
                  }
        return render(request, self.template_name, context)

