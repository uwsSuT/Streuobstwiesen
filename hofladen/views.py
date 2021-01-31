from django.shortcuts import render
from django.views.generic import TemplateView
from django_tables2 import SingleTableView

import os
from os.path import join, exists, isdir
from pprint import pformat

from hofladen.hofladen import HofladenCl
from hofladen.models import Hofladen, HofRubrik, Unterrubrik
from hofladen.tables import HofladenTable

class HofladenLinkIn(TemplateView):

    def get_menu_entrys(self, context, hofl):
        context['rubriken'] = hofl.get_rubriken()
        context['unterrubriken'] = hofl.get_unterrubriken()
        context['OekoSiegel'] = hofl.get_oeko_siegel()

class HofladenView(HofladenLinkIn, SingleTableView):
    """
        ziemlich trickreicher View der mit mehreren
        verschiedenen URL Definitionen aufgerufen wird.

        Je nach Argument werden die Höfe,
        abhängig von der Rubrik und UnterRubriken geholt
        und damit eine Tabelle (siehe tables.py) gefüllt.
    """
    template_name = "hofladen/hofladen_view.html" # MAP-View
    def get(self, request, rid=0, uid=0, bio=False, sid=0, unverpackt=0,
            *args, **kwargs):
#        print("HofladenView: rid: %s, uid: %s, bio:%s sid: %s unverp: %s " % (
#               rid, uid, bio, sid, unverpackt))
        context = {}
        hofl = HofladenCl(verbose=0)
        self.get_menu_entrys(context, hofl)

        hofladen_list = []
        if rid:
            context['rubrik'] = HofRubrik.objects.get(id=rid)
            hofladen_list = HofRubrik.objects.get(id=rid).hofladen_list
        if uid:
            context['Artikel'] = Unterrubrik.objects.get(id=uid)
            hofladen_list = Unterrubrik.objects.get(id=uid).hofladen_list
        if bio:
            context['BIO'] = True
            if sid:
                uid = sid
                hofladen_list = Unterrubrik.objects.get(id=sid).hofladen_list
            else:
                hofladen_list = HofRubrik.objects.get(id=hofl.BioID).hofladen_list
        if unverpackt:
            context['UNVERPACKT'] = True
            hofladen_list = HofRubrik.objects.get(id=hofl.UnverpacktID).hofladen_list

        context["markers"] = hofl.get_geo_objects(
            rubrik_id=rid,
            urubrik_id=uid,
            bio=bio,
            unverpackt=unverpackt)

        if not hofladen_list:
            # Alle Hoefe sollen angezeigt werden
            hoefe = Hofladen.objects.all().order_by('name')
        else:
            hoefe = []
            for hof_id in hofladen_list:
                hoefe.append(Hofladen.objects.get(id=hof_id))

        context['table'] = HofladenTable(hoefe)
        return render(request, self.template_name, context)
