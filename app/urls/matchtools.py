""" urls.matchtools - URLs under matchtools/ associated with matching tools
    imported by urls.__init__ as part of urls subpackage
"""

from django.urls import path

from matchtools.views import (
    trait_match_list, match_operation_endpoint, source_attribute_edit
    # trait_match
)

urlpatterns = [
    path('tm/', trait_match_list, name="info-trait-match"),
    path('match_operation/', match_operation_endpoint, name='match_operation_endpoint'),
    # path('tm/<int:source_attribute_id>', trait_match, name="trait-match")
    path('source_attribute_modify/', source_attribute_edit, name='source_attribute_edit')
]
