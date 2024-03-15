""" urls.matchtools - URLs under matchtools/ associated with matching tools
    imported by urls.__init__ as part of urls subpackage
"""

from django.urls import path

from matchtools.views import (
    info_traitmatch, trait_match
)

urlpatterns = [
    path('tm/', info_traitmatch, name="info-trait-match"),
    path('tm/1', trait_match, name="trait-match") #path TODO
]
