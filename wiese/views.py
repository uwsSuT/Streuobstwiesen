from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from .forms import WieseModelForm, WiesenUpdateForm
from obstsorten.models import Wiese

import os
from os.path import join
from pprint import pformat

APP = 'wiese'

class WieseObjectMixin(object):
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


class WieseListView(View):
    #
    # Darstellung aller Obst-Wiesen mit Karte und Lister der definierten Wiesen
    #
    template_name = "wiese/wiese_list.html"

    def get_queryset(self):
        return Wiese.objects.all()

    def get(self, request, *args, **kwargs):
        #
        # mögliche Verbesserungen: 
        # - Anzahl Bäume
        # - dynamisches ermitteln des Grafik-Namens
        #
        context = {'wiesen_list': self.get_queryset(),
                   'grafik' : 'images/wiese/Hilgh_StreuobstWiesen_2020_07.png',
                  }
        return render(request, self.template_name, context)

class WieseView(WieseObjectMixin, View):
    template_name = "wiese/wiese_detail.html" # DetailView
    def __find_grafik__(self, wid):
        """
            such die zur wiesen_id zugehörige Grafik in dem Static Verzeichnis
        """
        pwd = os.getcwd()
        for f in os.listdir(join(pwd, 'static', 'images', APP)):
            if f.find("%s_" % wid) == 0:
                return join('images', APP, f)

    def get(self, request, wiesen_id=None, *args, **kwargs):
        # GET method
        context = {'object': self.get_object(wiesen_id=self.kwargs.get('id')),
                   'grafik' : self.__find_grafik__(self.kwargs.get('id')),
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

class ObstWiesenView(View):
    template_name = "wiese/obstwiesen.html" # Obstwiesen Überblick

    def get(self, request, *args, **kwargs):
        context = {'grafik' : 'image/wiese/Hilgh_StreuobstWiesen_2020_07.png'}
        return render(request, self.template_name, context)
