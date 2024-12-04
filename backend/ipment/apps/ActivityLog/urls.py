from django.urls import re_path as url
from apps.ActivityLog.views import ActivityLogView

urlpatterns = [
    # Activity Log URL
    url(r'^(?P<method>list-auth|view-auth)/log/$', ActivityLogView.activityLogApi),
    url(r'^(?P<method>list-act|view-act)/log/$', ActivityLogView.activityLogApi),
    url(r'^view-auth/log/(?P<id>[0-9]+)$', ActivityLogView.activityLogApi),
    url(r'^view-act/log/(?P<id>[0-9]+)$', ActivityLogView.activityLogApi)
]