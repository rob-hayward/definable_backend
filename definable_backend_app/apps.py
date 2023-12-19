from django.apps import AppConfig


class DefinableBackendAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'definable_backend_app'
