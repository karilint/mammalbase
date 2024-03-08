""" urls.debug_toolbar - Urls needed for Debug Toolbar middleware
    imported by urls.__init__ as part of urls subpackage
    
    https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
"""
from django.urls import path, include
from debug_toolbar import urls as debug_toolbar_urls

urlpatterns = [
    path('__debug__/', include(debug_toolbar_urls))
]