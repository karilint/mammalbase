""" urls.root - URLs directry under root of server
    for example landing page, about, history etc
    imported by urls.__init__ as part of urls subpackage
"""
from django.urls import path

from mb.views import (
    index,
    index_about,
    about_history,
    index_news,
    privacy_policy)

urlpatterns = [
    path('', index, name='index'),
    path('mb', index, name='index'),
    path('index_about', index_about, name='index_about'),
    path('about_history', about_history, name='about_history'),
    path('news', index_news, name='index_news'),
    path('privacy_policy', privacy_policy, name='privacy_policy'),
]
