from django.urls import path

from . import views

urlpatterns = [
    path('lm/', views.location_matchtool, name="location-matchtool"),
]