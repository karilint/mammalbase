""" mb.views.index - Static index and error page views can be found here

Please import from subpackage (for example):

from mb.views import index_news
"""
from django.shortcuts import render

# Error Pages
# https://blog.khophi.co/get-django-custom-error-views-right-first-time/
def server_error(request):
    return render(request, 'errors/500.html')

def not_found(request):
    return render(request, 'errors/404.html')

def permission_denied(request):
    return render(request, 'errors/403.html')

def bad_request(request):
    return render(request, 'errors/400.html')

def about_history(request):
    return render(request, 'mb/history.html',)

def index_about(request):
    return render(request, 'mb/index_about.html',)

def privacy_policy(request):
    return render(request, 'mb/privacy_policy.html',)

#@ratelimit(key='ip', rate='2/m')
def index(request):
    return render(request, 'mb/index.html',)

def index_news(request):
    return render(request, 'mb/index_news.html',)
