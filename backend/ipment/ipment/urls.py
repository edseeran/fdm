from django.contrib import admin
from django.urls import include, path, include, re_path as url


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'UserAccount/', include('apps.UserAccount.urls')),
    url(r'iPM/', include('apps.iPM.urls')),
    url(r'Configuration/', include('apps.Configuration.urls')),
    url(r'ActivityLog/', include('apps.ActivityLog.urls')),
]
