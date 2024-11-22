from django.apps import AppConfig


class MydefaultappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MyDefaultApp'
