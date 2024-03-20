from django.urls import path

from . import views

urlpatterns = [
    path('tm/', views.trait_match, name="trait-match"),
    path('lm/', views.source_location_list, name="location-match"),
]