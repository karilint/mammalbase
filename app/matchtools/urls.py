from django.urls import path

from . import views

urlpatterns = [
    path('tm/', views.trait_match, name="trait-match"),
    path('lm/', views.location_matchtool, name="location-matchtool"),
]