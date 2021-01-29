from django.urls import path

from .views import HofladenView

app_name = 'hofladen'

urlpatterns = [
	path('bio-view/<int:bio>/<int:sid>/', HofladenView.as_view(), name='bio-view'),
	path('bio-view/<int:bio>', HofladenView.as_view(), name='bio-view'),
	path('unverp-view/<int:unverpackt>', HofladenView.as_view(), name='unverp-view'),
	path('hofladen-view/<int:rid>/', HofladenView.as_view(), name='hofladen-view'),
	path('hofladen-view/<int:rid>/<int:uid>/', HofladenView.as_view(), name='hofladen-view'),
	path('', HofladenView.as_view(), name='hofladen-view'),
]