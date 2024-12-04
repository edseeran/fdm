from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from apps.UserAccount.models import UserProfile
from apps.ActivityLog.models import ActivityLog  # Import ActivityLog model
import json  # Import json module

# Signal to automatically create a UserProfile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create a UserProfile when a new User is created.
    Also logs the creation of the UserProfile in the ActivityLog.
    """
    if created:
        # Create UserProfile
        user_profile = UserProfile.objects.create(user=instance)

        # Log the creation of UserProfile
        ActivityLog.objects.create(
            user=instance,  # The user who was created
            method='create',
            module='UserAccount',
            model='UserProfile',
            record_id=user_profile.id,
            changes='New Record'
        )

# Signal to log the deletion of UserProfile before it's deleted
@receiver(pre_delete, sender=UserProfile)
def log_userprofile_delete(sender, instance, **kwargs):
    """
    Signal handler to log the deletion of a UserProfile before it's deleted.
    """
    # Log the deletion of UserProfile
    ActivityLog.objects.create(
        user=instance.user,
        method='delete',
        module='UserAccount',
        model='UserProfile',
        record_id=instance.id,
        changes='Record Deleted'
    )
