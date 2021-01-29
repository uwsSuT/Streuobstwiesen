from django.shortcuts import render
from django.views.generic import TemplateView

import os
from os.path import join, exists, isdir
from django.contrib.staticfiles.finders import FileSystemFinder
from pprint import pformat

from hofladen.hofladen import HofladenCl
from hofladen.models import Hofladen, HofRubrik, Unterrubrik

class HofladenLinkIn(TemplateView):

	def get_menu_entrys(self, context, hofl):
		context['rubriken'] = hofl.get_rubriken()
		context['unterrubriken'] = hofl.get_unterrubriken()
		context['OekoSiegel'] = hofl.get_oeko_siegel()

class HofladenView(HofladenLinkIn):
	template_name = "hofladen/hofladen_view.html" # MAP-View
	
	def get_context_data(self, **kwargs):
		"""Return the view context data."""

		context = super().get_context_data(**kwargs)
	
		hofl = HofladenCl(verbose=1)
		self.get_menu_entrys(context, hofl)

		rubrik_id = 0
		urubrik_id = 0
		if 'id' in kwargs:
			rubrik_id = kwargs['id']
			context['rubrik'] = HofRubrik.objects.get(id=rubrik_id)
		if 'uid' in kwargs:
			urubrik_id = kwargs['uid']
			context['Artikel'] = Unterrubrik.objects.get(id=urubrik_id)

		context["markers"] = hofl.get_geo_objects(rubrik_id=rubrik_id, urubrik_id=urubrik_id)
		
		return context

class BioView(HofladenLinkIn):
	template_name = "hofladen/hofladen_view.html" # MAP-View
	
	def get_context_data(self, **kwargs):
		"""Return the view context data."""

		context = super().get_context_data(**kwargs)
	
		hofl = HofladenCl(verbose=1)
		self.get_menu_entrys(context, hofl)

		context['BIO'] = True
		siegel_id = 0
		if 'id' in kwargs:
			siegel_id = kwargs['id']
			context['BioSiegel'] = Unterrubrik.objects.get(id=siegel_id)

		context["markers"] = hofl.get_geo_objects(bio=True, urubrik_id=siegel_id)
		
		return context

class UnverpacktView(HofladenLinkIn):
	template_name = "hofladen/hofladen_view.html" # MAP-View
	
	def get_context_data(self, **kwargs):
		"""Return the view context data."""

		context = super().get_context_data(**kwargs)
	
		hofl = HofladenCl(verbose=1)
		self.get_menu_entrys(context, hofl)

		hofl.verbose=2

		context['UNVERPACKT'] = True
		context["markers"] = hofl.get_geo_objects(unverpackt=True)

		return context