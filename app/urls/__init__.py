""" All the URLs are configured here.

This subpackage contains all url related information.

After successful import urlpatterns variable should contain all the path
information for the urls.

https://docs.djangoproject.com/en/3.2/topics/http/urls/

For example:

urlpatterns = [
    path('page.html', page_view_function),
    path('textpage.html', TextPage.as_view()),
    path('path/' include('submodule.with_more_urlpatterns'))
]
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static as static_url
from django.urls import path, include


urlpatterns = [
    path('', include('urls.root')),
    path('', include('urls.diets')),
    path('', include('urls.debug_toolbar')),
    path('', include('urls.unsorted')),
    path('import/', include('urls.imports')),
    path('exports/', include('urls.exports')),

    path('admin/', admin.site.urls),
    path('select2/', include('django_select2.urls')),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static_url(
            settings.MEDIA_URL,
            document_root=settings.MEDIA_ROOT)

handler404 = 'main.views.not_found'
handler500 = 'main.views.server_error'
handler403 = 'main.views.permission_denied'
handler400 = 'main.views.bad_request'
