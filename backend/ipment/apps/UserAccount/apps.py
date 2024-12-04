from django.apps import AppConfig

class UserAccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.UserAccount'

    def ready(self):
        import apps.UserAccount.signals  # Import the signals when the app is ready
