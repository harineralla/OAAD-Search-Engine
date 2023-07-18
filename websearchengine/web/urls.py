from django.urls import path

from . import views
from .views import SearchView

urlpatterns = [
    path("", views.index, name="index"),
    path('search/', SearchView.as_view(), name='search'),
    path('search/sorted/', SearchView.sort_query_results, name='sort'),
    path('autocomplete/', SearchView.as_view(), name='autocomplete'),
]
