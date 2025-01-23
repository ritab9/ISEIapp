from django.apps import AppConfig

class AprConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apr'
    def ready(self):
        import apr.signals