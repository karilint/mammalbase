""" urls.exports - URLs accosiated with exporting data
    imported by urls.__init__ as part of urls subpackage
"""

from django.urls import path

from exports.views import (
    export_to_tsv,
    get_exported_file,
    form_submitted)

urlpatterns = [
    path('ETS', export_to_tsv, name='ets'),
    path('get_file/<int:file_id>', get_exported_file, name='getfile'),
    path('submitted', form_submitted, name='submission')
]
