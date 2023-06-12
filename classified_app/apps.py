from django.apps import AppConfig


class ClassifiedAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'classified_app'
    
    def ready(self):
        from . import signals
