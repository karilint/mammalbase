""" urls.matchtools - URLs under matchtools/ associated with matching tools
    imported by urls.__init__ as part of urls subpackage
"""

from django.urls import path

from matchtools.views import (
    trait_match_list, match_operation_endpoint, new_match_endpoint, source_location_list, location_match_detail, match_location
)

urlpatterns = [
    path('tm/', trait_match_list, name="trait_match_list"),
    path('match_operation/', match_operation_endpoint, name='match_operation_endpoint'),
    path('new_match/', new_match_endpoint, name='new_match_endpoint'),
    path('lm/', source_location_list, name="location-match"),
    path('lm/<int:id>', location_match_detail, name="location-match-detail"),
    path('match_location/', match_location, name="match_location"),
]
