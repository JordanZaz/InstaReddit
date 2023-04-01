from django.apps import AppConfig


class GorlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gorl'

    def ready(self):
        import gorl.signals
