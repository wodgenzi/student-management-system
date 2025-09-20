from django.urls import path
from . import views

urlpatterns = [
    path('update-profile-settings/', views.update_profile_settings, name="update-profile-settings"),
]