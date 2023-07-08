from django.urls import path

from . import views
from .views import SearchView

urlpatterns = [
    path("", views.index, name="index"),
    path('search/', SearchView.as_view(), name='search'),
    path('autocomplete/', SearchView.as_view(), name='autocomplete'),
]
