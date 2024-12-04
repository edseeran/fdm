from django.urls import re_path as url, path
from apps.UserAccount.views import UserView, GroupView, PermissionView, AuthenticationView, UserProfileView, UserNameView

urlpatterns = [
    # User URLS
    url(r'^(?P<method>create|list|view|update|delete)/user/$', UserView.userApi),
    url(r'^view/user/(?P<id>[0-9]+)$', UserView.userApi),
    
    # User Profile URLS
    url(r'^(?P<method>create|list|view|update|delete)/user-profile/$', UserProfileView.userProfileApi),
    url(r'^view/user-profile/(?P<id>[0-9]+)$', UserProfileView.userProfileApi),
    
    # User Name URLS
    url(r'^(?P<method>create|list|view|update|delete)/user-name/$', UserNameView.userNameApi),
    url(r'^view/user-name/(?P<id>[0-9]+)$', UserNameView.userNameApi),

    # Group URLS
    url(r'^(?P<method>create|list|view|update|delete)/group/$', GroupView.groupApi),
    url(r'^view/group/(?P<id>[0-9]+)$', GroupView.groupApi),

    # Permission URLS
    url(r'^(?P<method>list|view)/permission/$', PermissionView.permissionApi),
    url(r'^view/permission/(?P<id>[0-9]+)$', PermissionView.permissionApi),

    path('login/', AuthenticationView.LoginAPIView.as_view(), name='api-login'),
    path('check-login/', AuthenticationView.CheckLoggedInAPIView.as_view(), name='api-check-login'),
    path('logout/', AuthenticationView.LogoutAPIView.as_view(), name='api-logout'),


]