from django.urls import path

from .views import (
		HofladenView,
	)

app_name = 'hofladen'

urlpatterns = [
	path('', HofladenView.as_view(), name='hofladen-view'),
]