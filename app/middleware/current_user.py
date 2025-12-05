# middleware/current_user.py

import threading

_user = threading.local()

def get_current_user():
    return getattr(_user, 'value', None)

class CurrentUserMiddleware:
    """Middleware to save request.user in thread local storage"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = request.user
        response = self.get_response(request)
        return response
