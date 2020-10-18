from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django_tables2 import SingleTableView, SingleTableMixin
from django.views import View

from .forms import WieseModelForm, WiesenUpdateForm
from obstsorten.models import Wiese, ObstBaum, ObstSorten
from obstsorten.views import ObstLinkIn
from wiese.tables import WiesenTable

import os
from os.path import join, exists, isdir
from pprint import pformat

APP = 'wiese'

class WieseObjectMixin(ObstLinkIn, object):
    model = Wiese
    def get_object(self, wiesen_id=None):
        obj = None
        if wiesen_id is not None:
            obj = get_object_or_404(self.model, wiesen_id=wiesen_id)
        return obj

class WieseCreateView(View):
    template_name = "wiese/wiese_create.html" # DetailView
    def get(self, request, *args, **kwargs):
        # GET method
        form = WieseModelForm()
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # POST method
        form = WieseModelForm(request.POST, request.FILES or None)

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

#    def get_queryset(self):
#        return Wiese.objects.all().order_by('name')
#
#    def get(self, request, *args, **kwargs):
#        #
#        # mögliche Verbesserungen: 
#        # - Anzahl Bäume
#        # - dynamisches ermitteln des Grafik-Namens
#        #
#        context = {'wiesen_list': self.get_queryset(),
#                   'grafik' : 'images/wiese/Hilgh_StreuobstWiesen_2020_09.png',
#                   'obstsorten_menu' : self.get_Obst_menu(),
#                  }
#        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grafik'] ='images/wiese/Hilgh_StreuobstWiesen_2020_09.png'
        context['obstsorten_menu'] = self.get_Obst_menu()

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
            if f.find("%s_" % wid) == 0:
                return join('images', APP, f)

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

    def get(self, request, wiesen_id=None, *args, **kwargs):
        # GET method
        context = {
           'object': self.get_object(wiesen_id=self.kwargs.get('id')),
           'grafik' : self.__find_grafik__(self.kwargs.get('id')),
           'trees' : self.__find_trees__(self.kwargs.get('id')),
           'wiesen_list' : Wiese.objects.all().order_by('name'),
           'obstsorten_list' : ObstSorten.objects.all().order_by('sorten_id'),
           'obstsorten_menu' : self.get_Obst_menu(),
           }
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
            print("Could not find: %s" % bdir)
            return []

        for f in os.listdir(join(pwd, 'static', 'images', 'baum')):
            if isdir(join(pwd, 'static', 'images', 'baum', f)) and \
                    f == wiesen_name:
                print("FOUND Dir: %s" % f)
                for b in os.listdir(join(pwd, 'static', 'images', 'baum', f)):
                    if b.find("%s_" % baum.baum_id) == 0:
                        print("FOUND Tree: %s" % b)
                        baum_pics.append(join('images', 'baum', f, b))

            elif f.find("%s_" % baum.baum_id) == 0:
                baum_pics.append(join('images', 'baum', f))
        return baum_pics

    def __find_trees__(self, wid):
        """
            Suche alle Baäume der Wiese, die sollen unterhalb des Bildes
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

    def get(self, request, wiesen_id=None, *args, **kwargs):
        # GET method
        # print("baum-detail: %s" % self.kwargs.get('id'))
        baum = ObstBaum.objects.get(baum_id=self.kwargs.get('id'))
        wiesen_name = Wiese.objects.get(wiesen_id=baum.wiese_id).name
        context = {
           'baum_pics'  : self.__find_pics__(baum, wiesen_name),
           'baum_infos' : baum,
           'sorte'      : ObstSorten.objects.get(sorten_id=baum.sorten_id_id),
           'wiese'      : wiesen_name,
           'obstsorten_menu' : self.get_Obst_menu(),
          }
        return render(request, self.template_name, context)

class BaumPicView(WieseObjectMixin, View):
    """
        Zeig nur das Bild des Baumes, aber in voller Größe
    """
    template_name = "wiese/baum_pic.html" # BaumView
    def get(self, request, pic=None, *args, **kwargs):
        # GET method
        print("baum-pic: %s" % self.kwargs.get('pic'))
        context = {
                   'baum_pic'  : self.kwargs.get('pic'),
                   'obstsorten_menu' : self.get_Obst_menu(),
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
            #if form.is_valid():
            form.save(update_fields=['grafik'])
            context['object'] = obj
            context['form'] = form
        return render(request, self.template_name, context)


class WieseDeleteView(WieseObjectMixin, View):
    template_name = "wiese/wiese_delete.html" # DetailView
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
