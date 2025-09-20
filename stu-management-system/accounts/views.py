import json
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from . import models

def logout_view(request):
    logout(request)
    return redirect('login')  # or any URL name you want


class CustomLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

@csrf_exempt
def update_profile_settings(request):
    if request.method == 'POST':
        user = request.user
        profile = models.Profile.objects.get(user=user)
        settings = profile.settings
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
        settings.filter_start_date = data.get('start_date')
        settings.filter_end_date = data.get('end_date')
        settings.filter_statuses = data.get('statuses', '')
        settings.save()
        return HttpResponse("Settings updated successfully.")

