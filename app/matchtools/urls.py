from django.urls import path

from . import views

urlpatterns = [
    path('traitmatch/', views.trait_match, name="trait-match"),
]
