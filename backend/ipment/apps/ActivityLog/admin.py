from django.contrib import admin
from .models import ActivityLog, LoginActivity

admin.site.register(ActivityLog)
admin.site.register(LoginActivity)