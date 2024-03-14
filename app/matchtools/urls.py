from django.urls import path

from . import views

urlpatterns = [
    path('tm/', views.trait_match, name="trait-match"),
    path('sl/', views.source_location_list, name="source-location-list"),
]