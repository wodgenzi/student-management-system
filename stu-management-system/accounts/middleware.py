from django.shortcuts import redirect
from django.conf import settings

LOGIN_URL = getattr(settings, 'LOGIN_URL', '/login/')
EXEMPT_URLS = [LOGIN_URL.lstrip('/'), 'admin/login/']

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            if path not in EXEMPT_URLS:
                return redirect(f'{LOGIN_URL}')
        return self.get_response(request)