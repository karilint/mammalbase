""" urls.matchtools - URLs under matchtools/ associated with matching tools
    imported by urls.__init__ as part of urls subpackage
"""

from django.urls import path

from matchtools.views import (
    trait_match_list, match_operation_endpoint, new_match_endpoint
)

urlpatterns = [
    path('tm/', trait_match_list, name="trait_match_list"),
    path('match_operation/', match_operation_endpoint, name='match_operation_endpoint'),
    path('new_match/', new_match_endpoint, name='new_match_endpoint'),
]
