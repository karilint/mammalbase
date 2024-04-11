from django.urls import path

from . import views

urlpatterns = [
    path('tm/', views.trait_match, name="trait-match"),
    path('lm/', views.source_location_list, name="location-match"),
    path('lm/<int:id>', views.location_match_detail, name="location-match-detail"),
    path('match_location/', views.match_location, name="match_location"),
]