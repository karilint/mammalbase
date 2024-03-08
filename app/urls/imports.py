""" urls.imports - URLs accosiated with data importing
    imported by urls.__init__ as part of urls subpackage
"""
from django.urls import path

from imports.views import (
    import_diet_set,
    import_ets,
    import_occurrences,
    import_proximate_analysis)

urlpatterns = [
    path(
            'diet_set',
            import_diet_set,
            name='import_diet_set'),
    path(
            'ets',
            import_ets,
            name='import_ets'),
    path(
            'occurrences',
            import_occurrences,
            name='import_occurrences'),
    path(
            'proximate_analysis',
            import_proximate_analysis,
            name='import_proximate_analysis'),
]
