import os
from os.path import join
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableView, SingleTableMixin
from django_tables2.config import RequestConfig
from django_tables2.export.export import TableExport
from django_tables2.export.views import ExportMixin

from obstsorten.models import Wiese, ObstBaum, ObstSorten
from obstsorten.defs import Obst_Type
from baeume.baeume import BaumLeaflet
from baeume.tables import BaumInfosTable
from baeume.filters import BaumInfosFilter

DEBUG = int(os.environ.get('DEBUG'))

APP = 'obstsorten'

class HomePageView(TemplateView):
    template_name = 'home.html'


class AboutPageView(TemplateView):
    template_name = 'about.html'

    def get(self, request, *args, **kwargs):
        from hilgi import Version, Datum
        context = { 'VERSION' : Version,
                    'DATUM'   : Datum,
                  }
        return render(request, self.template_name, context)

class ObstLinkIn(object):
    obst = ObstSorten.objects.all().order_by('obst_sorte')

    def get_Obst_menu(self):
        """
            generier ein zwei-dimensionales Dictionary mit
            Obstsorten-Type : ObstSorte
        """
        obst_menu = []
        obst_sorten_menu = {}
        for os in self.obst:
            otype = Obst_Type[os.obst_type]
            if otype.lower() == 'unbekannt' or \
               otype.lower() == 'tod':
                continue
            elif not otype in obst_sorten_menu:
                obst_sorten_menu[otype] = [os.obst_sorte]
            else:
                obst_sorten_menu[otype].append(os.obst_sorte)
        for o in sorted(obst_sorten_menu.keys()):
            os = {
                    'name': o,
                    'obstsorten' : obst_sorten_menu[o],
                 }
            obst_menu.append(os)
        return obst_menu

class ObstSortenView(ObstLinkIn, TemplateView):
    template_name = 'obstsorten.html'

    def __find_grafik__(self, oid):
        """
            such die zur Obstsorte zugeh??rige Grafik in dem Static Verzeichnis
        """
        pwd = os.getcwd()
        for f in os.listdir(join(pwd, 'static', 'images', APP)):
            if f.find("%s_" % oid) == 0:
                #print("OBST-BILD gefunden %s" % f)
                return join('images', APP, f)

    def get_queryset(self):
        # obst = ObstSorten.objects.all().order_by('sorten_id')
        robst = []
        for oid in range(0,len(Obst_Type)):
            # hol immer nur die Obstsorten f??r den Type
            if Obst_Type[oid] == 'unbekannt' or \
                    Obst_Type[oid] == 'Tod':
                        continue
            obst = ObstSorten.objects.filter(obst_type=oid).order_by('obst_sorte')
            for o in obst:
                if 'unbestimmt' in o.obst_sorte:
                    continue
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
                   'obstsorten_menu' : self.get_Obst_menu(),
                  }
        return render(request, self.template_name, context)

class ObstSortenDetView(ObstLinkIn, TemplateView):
    template_name = 'obstsorten_detail.html'

    def __find_grafik__(self, oid):
        """
            such die zur Obstsorte zugeh??rige Grafik in dem Static Verzeichnis
        """
        pwd = os.getcwd()
        for f in os.listdir(join(pwd, 'static', 'images', APP)):
            if f.find("%s_" % oid) == 0:
                #print("OBST-BILD gefunden %s" % f)
                return join('images', APP, f)

    def get_queryset(self):
        o = ObstSorten.objects.get(obst_sorte=self.kwargs.get('sorte'))
        sorte = {
            'obst_type'       : Obst_Type[o.obst_type],
            'obst_sorte'      : o.obst_sorte,
            'pflueck_reif'    : o.pflueck_reif,
            'verwendung'      : o.verwendung,
            'geschmack'       : o.geschmack,
            'lagerfaehigkeit' : o.lagerfaehigkeit,
            'alergie_info'    : o.alergie_info,
            'www'             : o.www,
            'picture'         : self.__find_grafik__(o.sorten_id),
            'sorten_id'       : o.sorten_id,
            }
        return sorte

    def find_wiesen(self, sorten_id):
        """
            hole alle Wiesen auf der diese Obst-Sorte w??chst
            hierzu m??ssen wir zun??chst alle B??ume vom Type finden
            in deren Elementen sind die Wiesen-Ids enthalten
        """
        wiesen = {}
        for baum in ObstBaum.objects.filter(sorten_id=sorten_id):
            wiese = Wiese.objects.get(wiesen_id=baum.wiese_id)
            if wiese.name not in wiesen:
                wiesen[wiese.www_name] = wiese.wiesen_id
        return wiesen



    def get(self, request, sid=None, *args, **kwargs):
        # GET method
        ob = self.get_queryset()
        baeume = BaumLeaflet()

        context = {'object': ob,
                   'wiesen_sorte'    : self.find_wiesen(ob['sorten_id']),
                   'wiesen_list'     : Wiese.objects.all().order_by('wiesen_id'),
                   'obstsorten_list' : ObstSorten.objects.all().order_by('sorten_id'),
                   'baeume'          : baeume.get_geo_objects4sorte(ob['sorten_id']),
                   'obstsorten_menu' : self.get_Obst_menu(),
                  }
        return render(request, self.template_name, context)

class BaumInfosView(ObstLinkIn, SingleTableMixin, FilterView):

    model = ObstBaum
    table_class = BaumInfosTable
    filterset_class = BaumInfosFilter
    template_name = "baum_infos.html"
