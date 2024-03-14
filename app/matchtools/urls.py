from django.urls import path

from . import views

urlpatterns = [
    path('tm/', views.trait_match, name="trait-match"),
    path('lm/', views.location_matchtool, name="location-matchtool"),
    path('lmd/', views.location_match_detail, name="location-match-detail"),
    path('match_location/', views.match_location, name="match_location"),
]