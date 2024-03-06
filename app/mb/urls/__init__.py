from django.urls import path, include

urlpatterns = [
    path('', include('mb.urls.main')),
    path('', include('mb.urls.debug_toolbar')),
    path('', include('mb.urls.unsorted')),
    path('exports/', include('exports.urls')),
]
