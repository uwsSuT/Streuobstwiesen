from django.urls import path

from .views import HomePageView, AboutPageView, ObstSortenView 


urlpatterns = [
    path('about/', AboutPageView.as_view(), name='about'), 
    path('', HomePageView.as_view(), name='home'),
    path('obstsorten', ObstSortenView.as_view(), name='obstsorten'),
]
