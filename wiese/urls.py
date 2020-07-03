from django.urls import path
from .views import (
        WieseCreateView,
        WieseDeleteView,
        WieseListView,
        WieseView,
        WieseUpdateView
)

app_name = 'wiese'

urlpatterns = [
    path('', WieseListView.as_view(), name='wiesen-list'),
    path('<int:id>/', WieseView.as_view(), name='wiesen-detail'),
    path('create/', WieseCreateView.as_view(), name='wiesen-create'),
    path('update/<int:id>/', WieseUpdateView.as_view(), name='wiesen-update'),
    path('delete/<int:id>/', WieseDeleteView.as_view(), name='wiesen-delete'),
]
