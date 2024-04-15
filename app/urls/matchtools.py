""" urls.matchtools - URLs under matchtools/ associated with matching tools
    imported by urls.__init__ as part of urls subpackage
"""

from django.urls import path

from matchtools.views import (
    trait_match_list, match_operation_endpoint, source_attribute_edit, get_match_endpoint
)

urlpatterns = [
    path('tm/', trait_match_list, name="trait_match_list"),
    path('match_operation/', match_operation_endpoint, name='match_operation_endpoint'),
    path('source_attribute_modify/', source_attribute_edit, name='source_attribute_edit'),
    path('get_match/', get_match_endpoint, name='get_match_endpoint'),
]
