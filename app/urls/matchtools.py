""" urls.matchtools - URLs under matchtools/ associated with matching tools
    imported by urls.__init__ as part of urls subpackage
"""

from django.urls import path

from matchtools.views import (
    info_traitmatch, match_operation_endpoint
    # trait_match
)

urlpatterns = [
    path('tm/', info_traitmatch, name="info-trait-match"),
    path('match_operation/', match_operation_endpoint, name='match_operation_endpoint')
    # path('tm/<int:source_attribute_id>', trait_match, name="trait-match")
]
