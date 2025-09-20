from django.contrib.auth.models import User
from django.db import models

class UserSetting(models.Model):
    filter_start_date = models.DateField(null=True, blank=True)
    filter_end_date = models.DateField(null=True, blank=True)
    filter_order = models.CharField(max_length=20, default='-id')
    filter_statuses = models.CharField(max_length=100, blank=True, null=True)
class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    settings = models.OneToOneField(UserSetting, on_delete=models.CASCADE, default=None)
