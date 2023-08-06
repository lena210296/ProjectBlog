from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Blog'


class CeleryAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'celery_app'
