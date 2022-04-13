from django.urls import path

from .views import (
    HomePageView,
    AboutPageView,
    ObstSortenView,
    ObstSortenDetView,
    BaumInfosView,
)


urlpatterns = [
    path('about/', AboutPageView.as_view(), name='about'), 
    path('', HomePageView.as_view(), name='home'),
    path('obstsorten', ObstSortenView.as_view(), name='obstsorten'),
    path('baeume', BaumInfosView.as_view(), name='obstbaeume'),
    path('obstsorten_detail/<str:sorte>/', ObstSortenDetView.as_view(), name='obstsorten_detail'),
]
