from django.urls import path

from . import views

urlpatterns = [
    path('', views.export_hello_world, name='hello'),
]
