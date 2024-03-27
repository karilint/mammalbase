""" urls.matchtools - URLs under matchtools/ associated with matching tools
    imported by urls.__init__ as part of urls subpackage
"""

from django.urls import path

from matchtools.views import (
    trait_match_list, match_operation_endpoint
)

urlpatterns = [
    path('tm/', trait_match_list, name="info-trait-match"),
    path('match_operation/', match_operation_endpoint, name='match_operation_endpoint')
]
