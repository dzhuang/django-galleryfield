from django.apps import AppConfig


class DemoCustomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'demo_custom'

    def ready(self):
        import demo_custom.receivers  # noqa
