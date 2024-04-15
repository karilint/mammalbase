""" mb.views.index - Static index and error page views can be found here

Please import from subpackage (for example):

from mb.views import index_news
"""
from django.shortcuts import render

def index(request):
    """ This is the landing page on url / and /mb/ """
    return render(request, 'mb/index.html',)

def about_history(request):
    """ About, history in url /about_history """
    return render(request, 'mb/history.html',)

def index_about(request):
    """ At location /index_about """
    return render(request, 'mb/index_about.html',)

def privacy_policy(request):
    """ Renders at /privacy_policy """
    return render(request, 'mb/privacy_policy.html',)

def index_news(request):
    """ Main part of /news url """
    return render(request, 'mb/index_news.html',)


# Error Pages
# pylint: disable = missing-function-docstring
# Function names are now on quite selfexplanatory
def server_error(request):
    return render(request, 'errors/500.html')

def not_found(request):
    return render(request, 'errors/404.html')

def permission_denied(request):
    return render(request, 'errors/403.html')

def bad_request(request):
    return render(request, 'errors/400.html')
