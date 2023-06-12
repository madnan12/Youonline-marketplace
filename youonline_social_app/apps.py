from django.apps import AppConfig


class YouonlineSocialAppConfig(AppConfig):
    name = 'youonline_social_app'
    default_auto_field = 'django.db.models.BigAutoField'
    
    def ready(self):
        from . import signals