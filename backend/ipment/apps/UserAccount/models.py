from django.db import models
from django.contrib.auth.models import User, Group, Permission
from apps.iPM.models import Dashboard


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    phone = models.CharField(max_length=255, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    employee_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    department_team = models.CharField(max_length=255, blank=True, null=True)
    immediate_head_name = models.CharField(max_length=255, blank=True, null=True)
    immediate_head_phone = models.CharField(max_length=255, blank=True, null=True)
    dashboards = models.ManyToManyField(Dashboard, blank=True)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the time when created
    updated_at = models.DateTimeField(auto_now=True)      # Automatically update the time when saved

    def __str__(self):
        return self.user.username