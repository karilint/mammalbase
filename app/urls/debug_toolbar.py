from django.urls import path, include
from debug_toolbar import urls as debug_toolbar_urls

urlpatterns = [
    path('__debug__/', include(debug_toolbar_urls))
]