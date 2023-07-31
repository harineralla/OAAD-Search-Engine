from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('search/', views.SearchView.as_view(), name='search'),
    path('search/sorted/', views.SearchView.sort_query_results, name='sort'),
    path('headlines/', views.get_headlines, name='get_headlines')
]
