from django.urls import path

from .views import (
		HofladenView,
		BioView,
	)

app_name = 'hofladen'

urlpatterns = [
	path('bio-view/<int:id>/', BioView.as_view(), name='bio-view'),
	path('bio-view/', BioView.as_view(), name='bio-view'),
	path('hofladen-view/<int:id>/', HofladenView.as_view(), name='hofladen-view'),
	path('hofladen-view/<int:id>/<int:uid>/', HofladenView.as_view(), name='hofladen-view'),
	path('', HofladenView.as_view(), name='hofladen-view'),
]