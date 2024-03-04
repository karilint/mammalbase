from django.urls import path

from . import views

urlpatterns = [
    path('diet_set', views.import_diet_set, name='import_diet_set'),
    path('ets', views.import_ets, name='import_ets'),
    path('occurrences', views.import_occurrences, name='import_occurrences'),
    path('proximate_analysis', views.import_proximate_analysis, name='import_proximate_analysis'),
]
