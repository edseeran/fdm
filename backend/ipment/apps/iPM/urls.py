from django.urls import re_path as url
from apps.iPM.views import DashboardView, DataView

urlpatterns = [
    # Dashboard URLS
    url(r'^(?P<method>create|list|view|update|delete)/dashboard/$', DashboardView.dashboardApi),
    url(r'^view/dashboard/(?P<id>[0-9]+)$', DashboardView.dashboardApi),
    
    # Data URLS
    url(r'^(?P<method>list|list-top|list-circuit|delete)/data/$', DataView.dataApi)
]