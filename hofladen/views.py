from django.shortcuts import render
from django.views.generic import TemplateView

import os
from os.path import join, exists, isdir
from django.contrib.staticfiles.finders import FileSystemFinder
from pprint import pformat

from hofladen.hofladen import hofladen 

class HofladenView(TemplateView):
	template_name = "hofladen/hofladen_view.html" # MAP-View
	# template_name = "hofladen/newmap.html"
	
	def get_context_data(self, **kwargs):
		"""Return the view context data."""
		fF = FileSystemFinder(app_names='hofladen')

		context = super().get_context_data(**kwargs)
		hofl = hofladen(verbose=2)
		context["markers"] = hofl.get_geo_objects(fF.find("hofladen.geojson"))
		return context
