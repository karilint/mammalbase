from django.urls import path

from . import views

urlpatterns = [
    path('measurements', views.export_to_tsv, name='tsv'),
]
