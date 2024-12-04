from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import LoginActivity
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR') if request else 'Unknown IP'
    LoginActivity.objects.create(user=user, ip_address=ip, status='login', timestamp=now())
    logger.info(f"User {user.username} logged in from {ip}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR') if request else 'Unknown IP'
    
    if user:
        LoginActivity.objects.create(user=user, ip_address=ip, status='logout', timestamp=now())
        logger.info(f"User {user.username} logged out from {ip}")
    else:
        logger.info(f"Logout attempted from {ip} with no user session")

@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    ip = request.META.get('REMOTE_ADDR') if request else 'Unknown IP'
    failure_reason = "Invalid credentials"
    
    LoginActivity.objects.create(
        user=None, 
        ip_address=ip, 
        status='failed', 
        timestamp=now(), 
        failure_reason=failure_reason
    )
    
    logger.warning(f"Login failed from {ip} with username {credentials.get('username')}")
