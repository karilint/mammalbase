""" urls.diets - URLs accosiated with diets
    imported by urls.__init__ as part of urls subpackage
"""

from django.urls import path, include

from mb.views import (
    index_diet,
    diet_set_list,
    diet_set_detail,
    diet_set_delete,
    diet_set_edit,
    diet_set_item_detail,
    diet_set_item_delete,
    diet_set_item_edit,
    diet_set_item_new,
    diet_set_reference_list,
    food_item_list,
    food_item_detail,
    food_item_delete,
    food_item_edit,
)

urlpatterns = [
    path(
            'ids',
            index_diet,
            name='index_diet'),
    path(
            'ds/',
            diet_set_list,
            name='diet_set-list'),
    path(
            'dsr/',
            diet_set_reference_list,
            name='diet_set_reference-list'),
    path(
            'ds/<int:pk>/',
            diet_set_detail,
            name='diet_set-detail'),
    path(
            'ds/<int:pk>/delete/',
            diet_set_delete.as_view(),
            name='diet_set-delete'),
    path(
            'ds/<int:pk>/edit/',
            diet_set_edit,
            name='diet_set-edit'),
    path(
            'dsi/<int:pk>/',
            diet_set_item_detail,
            name='diet_set_item-detail'),
    path(
            'dsi/<int:pk>/delete/',
            diet_set_item_delete.as_view(),
            name='diet_set_item-delete'),
    path(
            'dsi/<int:pk>/edit/',
            diet_set_item_edit,
            name='diet_set_item-edit'),
    path(
            'dsi/new/<int:diet_set>/',
            diet_set_item_new,
            name='diet_set_item-new'),
    path(
            'fi/',
            food_item_list,
            name='food_item-list'),
    path(
            'fi/<int:pk>/',
            food_item_detail,
            name='food_item-detail'),
    path(
            'fi/<int:pk>/delete/',
            food_item_delete.as_view(),
            name='food_item-delete'),
    path(
            'fi/<int:pk>/edit/',
            food_item_edit,
            name='food_item-edit'),
]
