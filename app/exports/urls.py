from django.urls import path

from . import views

urlpatterns = [
    path('measurements', views.export_to_tsv, name='tsv'),
    path('get_file/<int:file_id>', views.get_exported_file, name='getfile'),
    path('submitted', views.form_submitted, name='submission')
]
