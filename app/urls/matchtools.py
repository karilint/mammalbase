""" urls.matchtools - URLs under matchtools/ associated with matching tools
    imported by urls.__init__ as part of urls subpackage
"""

from django.urls import path

from matchtools.views import (
    trait_match
)

urlpatterns = [
    path('tm/', trait_match, name="trait-match"),
]
