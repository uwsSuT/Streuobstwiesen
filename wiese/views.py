import os
from os.path import join, exists, isdir
from pprint import pformat

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import TemplateView, ListView
from django_tables2 import SingleTableView, SingleTableMixin
from django.views import View

from .forms import WieseModelForm, WiesenUpdateForm
from obstsorten.models import Wiese, ObstBaum, ObstSorten, Obst_Type
from obstsorten.views import ObstLinkIn
from wiese.tables import WiesenTable
from wiese.wiese import WiesenLeaflet
from baeume.baeume import BaumLeaflet
from hilgi.utils import BaumSessionClass

from init_db import  Streuobst_geo

DEBUG = int(os.environ.get('DEBUG', default=1))

APP = 'wiese'

class WieseObjectMixin(ObstLinkIn, object):
    model = Wiese
    def get_object(self, wiesen_id=None):
        obj = None
        if wiesen_id is not None:
            obj = get_object_or_404(self.model, wiesen_id=wiesen_id)
        return obj

    def set_dynamic(self, context):
        if not 'baeume_statisch' in self.request.session:
            context['baeume_statisch'] = ''
            context['baeume_dynamisch'] = "disabled"
        else:
            context['baeume_statisch'] = self.request.session['baeume_statisch']
            context['baeume_dynamisch'] = self.request.session['baeume_dynamisch']


class WieseCreateView(View):
    template_name = "wiese/wiese_create.html"
    def get(self, request, *args, **kwargs):
        # GET method
        form = WieseModelForm()
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # POST method
        form = WieseModelForm(request.POST, request.FILES or None)

        if DEBUG:
            print("request.FILES: %s" % pformat(request.FILES))
        if form.is_valid():
            form.save()
            form = WieseModelForm()
        context = {"form": form}
        return render(request, self.template_name, context)

class WieseListView(WieseObjectMixin, SingleTableMixin, ListView):
    #
    # Darstellung aller Obst-Wiesen mit Karte und Liste der definierten Wiesen
    #
    model = Wiese
    table_class = WiesenTable
    template_name = "wiese/wiese_list.html"

    def get_context_data(self, **kwargs):
        """
            Holt die ContextDaten vom Model und der WiesenTabelle
            wird hier noch mal um die dynamischen geo_objects
            und um die Menu-Entry erweitert
        """
        context = super().get_context_data(**kwargs)
        baeume = BaumLeaflet()
        wiesen = WiesenLeaflet(geo_json_file=Streuobst_geo)
        #print("WieseListView: dir: %s" % pformat(dir(self)))

        self.set_dynamic(context)

        #
        # Die beiden Parameter baeume und wiesen werden im JavaScript
        # verwendet
        #
        context["baeume"] = baeume.get_all_geo_objects()
        context["wiesen"] = wiesen.get_geo_objects()

        context['grafik'] ='images/wiese/Hilgh_StreuobstWiesen_2020_09.png'
        context['obstsorten_menu'] = self.get_Obst_menu()
        context['wiesen_list'] = Wiese.objects.all().order_by('name')

        return context

class WieseView(WieseObjectMixin, View):
    """
        Zeig eine Wiesen Grafik und
        deren darauf stehenden Bäume in einer darunter aufgeführten Liste
        die Liste enthält die Baum-Nr. mit einem URL-Link zum BaumView

    """
    template_name = "wiese/wiese_detail.html" # DetailView
    def __find_grafik__(self, wid):
        """
            such die zur wiesen_id zugehörige Grafik in dem Static Verzeichnis
        """
        pwd = os.getcwd()
        for f in os.listdir(join(pwd, 'static', 'images', APP)):
            if f.find("%s_" % wid) == 0 and \
               'png' in f.lower():
                return join('images', APP, f)
        return "NOT FOUND"

    def __find_trees__(self, wid):
        """
            Suche alle Bäume der Wiese, die sollen unterhalb des Bildes
            aufgelistet werden
        """
        trees = ObstBaum.objects.filter(wiese=wid).order_by('baum_id')
        ptrees = []
        for tree in trees:
            ptree = {
                'baum_id' : tree.baum_id,
                'name' : ObstSorten.objects.get(sorten_id=tree.sorten_id_id).obst_sorte,
                'zustand' : tree.zustand,
                'letzter_schnitt' : tree.letzter_schnitt,
                }
            #
            # Die '99' Nummer sind unbestimmte Bäume da fügen wird keine
            # URL ein
            #
            #if '99' not in "%s" % tree.sorten_id_id:
            ptree['url'] = tree.sorten_id_id
            ptrees.append(ptree)

        return ptrees

    def __get_geo_json_info__(self, wid):
        """
            Hol die GEO-JSON Info für die Wiese
        """
        geo_wiesen = WiesenLeaflet(geo_json_file=Streuobst_geo)
        wiese = Wiese.objects.get(wiesen_id=wid)
        geo_info = geo_wiesen.get_geo_info4wiese(wiese.www_name)

        #print("get_geo_json_info: %s" % pformat(geo_info))

        # In dem GEO-JSON vom GIS steckt ein MultiPolygon
        # wir können hier aber nur ein Polygon brauchen!
        #
        # zu allem Übel sind die Longitude und latitude Werte in dem
        # GEO-Json in der falschen Reihenfolge, also drehen wir die hier
        geo = []
        for point in geo_info['geometry']['coordinates'][0][0]:
            geo.append([point[1], point[0]])

        return geo

    def get(self, request, wid=None, *args, **kwargs):
        # GET method
        baeume = BaumLeaflet()
        context = {
            'object'          : self.get_object(wiesen_id=wid),
            'grafik'          : self.__find_grafik__(wid),
            'trees'           : self.__find_trees__(wid),
            'wiesen_list'     : Wiese.objects.all().order_by('name'),
            'obstsorten_list' : ObstSorten.objects.all().order_by('sorten_id'),
            'obstsorten_menu' : self.get_Obst_menu(),
            'baeume'          : baeume.get_all_trees4wiese(wid),
            'wiese_geo_info'  : self.__get_geo_json_info__(wid),
        }
        #print("Wiese-Detail: get <%s>" % pformat(baeume.geo_layers))
        self.set_dynamic(context)
        return render(request, self.template_name, context)

class BaumView(WieseObjectMixin, View):
    """
        Zeig alle Infos zu einem Baum
          - SortenInfos
          - Bilder
          - BaumInfos
    """
    template_name = "wiese/baum_detail.html" # BaumView
    def __find_pics__(self, baum, wiesen_name):
        """
            such die zur baum_id zugehörigen Bilder in dem Static Verzeichnis
            gib diese als Liste zurück
        """
        baum_pics = []
        pwd = os.getcwd()
        bdir = join(pwd, 'static', 'images', 'baum')
        if not exists(bdir):
            if DEBUG:
                print("Could not find: %s" % bdir)
            return []

        for f in os.listdir(join(pwd, 'static', 'images', 'baum')):
            if isdir(join(pwd, 'static', 'images', 'baum', f)) and \
                    f == wiesen_name:
                if DEBUG:
                    print("FOUND Dir: %s" % f)
                for b in os.listdir(join(pwd, 'static', 'images', 'baum', f)):
                    if b.find("%s_" % baum.baum_id) == 0:
                        if DEBUG:
                            print("FOUND Tree: %s" % b)
                        baum_pics.append(join('images', 'baum', f, b))

            elif f.find("%s_" % baum.baum_id) == 0:
                baum_pics.append(join('images', 'baum', f))
        return baum_pics

    def __find_trees__(self, wid):
        """
            Suche alle Bäume der Wiese, die sollen unterhalb des Bildes
            aufgelistet werden
        """
        trees = ObstBaum.objects.filter(wiese=wid).order_by('baum_id')
        ptrees = []
        for tree in trees:
            ptree = {
                'baum_id' : tree.baum_id,
                'name' : ObstSorten.objects.get(sorten_id=tree.sorten_id_id).obst_sorte,
                'zustand' : tree.zustand,
                'letzter_schnitt' : tree.letzter_schnitt,
                }
            #
            # Die '99' Nummer sind unbestimmte Bäume da fügen wird keine
            # URL ein
            #
            if '99' not in "%s" % tree.sorten_id_id:
                ptree['url'] = tree.sorten_id_id
            ptrees.append(ptree)

        return ptrees

    def __get_sorten_object__(self, id):
        o = ObstSorten.objects.get(sorten_id=id)
        sorte = {
            'obst_type'       : Obst_Type[o.obst_type],
            'obst_sorte'      : o.obst_sorte,
            'pflueck_reif'    : o.pflueck_reif,
            'verwendung'      : o.verwendung,
            'geschmack'       : o.geschmack,
            'lagerfaehigkeit' : o.lagerfaehigkeit,
            'alergie_info'    : o.alergie_info,
            'www'             : o.www,
            'sorten_id'       : o.sorten_id,
            }
        return sorte

    def get(self, request, wiesen_id=None, *args, **kwargs):
        # GET method
        # print("baum-detail: %s" % self.kwargs.get('id'))
        baum = ObstBaum.objects.get(baum_id=self.kwargs.get('id'))
        wo = Wiese.objects.get(wiesen_id=baum.wiese_id)
        context = {
            'baum_pics'  : self.__find_pics__(baum, wo.name),
            'baum_infos' : baum,
            'sorte'      : ObstSorten.objects.get(sorten_id=baum.sorten_id_id),
            'wiese'      : wo.www_name,
            'wid'        : baum.wiese_id,
            'obstsorten_menu' : self.get_Obst_menu(),
            'wiesen_list' : Wiese.objects.all().order_by('name'),
            'object'     : self.__get_sorten_object__(baum.sorten_id_id)
          }
        return render(request, self.template_name, context)

class BaumPicView(WieseObjectMixin, View):
    """
        Zeig nur das Bild des Baumes, aber in voller Größe
    """
    template_name = "wiese/baum_pic.html" # BaumView
    def get(self, request, pic=None, id=0, *args, **kwargs):
        # GET method
        if DEBUG:
            print("baum-pic: %s" % self.kwargs.get('pic'))
        baum = ObstBaum.objects.get(baum_id=id)
        context = {
           'baum_pic'  : self.kwargs.get('pic'),
           'baum_infos' : baum,
           'sorte' : ObstSorten.objects.get(sorten_id=baum.sorten_id_id),
           'obstsorten_menu' : self.get_Obst_menu(),
           'wiesen_list' : Wiese.objects.all().order_by('name'),
          }
        return render(request, self.template_name, context)

class WieseUpdateView(WieseObjectMixin, View):
    template_name = "wiese/wiese_update.html" # UpdateView
    def get_object(self):
        wiesen_id = self.kwargs.get('id')
        obj = None
        if wiesen_id is not None:
            obj = get_object_or_404(Wiese, wiesen_id=wiesen_id)
        return obj

    def get(self, request, wiesen_id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = WieseModelForm(instance=obj)
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object()
        if obj is not None:
            form = WieseModelForm(request.POST, request.FILES)
            form.save(update_fields=['grafik'])
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)


class WieseDeleteView(WieseObjectMixin, View):
    template_name = "wiese/wiese_delete.html"
    def get(self, request, wiesen_id=None, *args, **kwargs):
        # GET method
        context = {}
        obj = self.get_object(wiesen_id=self.kwargs.get('id'))
        if obj is not None:
            context['object'] = obj
        return render(request, self.template_name, context)

    def post(self, request, id=None,  *args, **kwargs):
        # POST method
        context = {}
        obj = self.get_object(wiesen_id=self.kwargs.get('id'))
        if obj is not None:
            obj.delete()
            context['object'] = None
            return redirect('/wiese/')
        return render(request, self.template_name, context)

class ObstWiesenView(WieseObjectMixin, View):
    template_name = "wiese/obstwiesen.html" # Obstwiesen Überblick

    def get(self, request, *args, **kwargs):
        context = {'grafik' : 'image/wiese/Hilgh_StreuobstWiesen_2020_09.png',
                   'obstsorten_menu' : self.get_Obst_menu(),
                  }
        return render(request, self.template_name, context)

def Set_dynamic_static_view(request, val):
    print("Set_dynamic_static_view: %s" % val)
    if val == 'dynamic':
        request.session['baeume_statisch'] = ""
        request.session['baeume_dynamisch'] = "disabled"
    else:
        request.session['baeume_statisch'] = "disabled"
        request.session['baeume_dynamisch'] = ""
    return redirect(reverse("wiese:wiesen-list"))
