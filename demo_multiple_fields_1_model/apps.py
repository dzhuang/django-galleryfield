from django.apps import AppConfig


class DemoCustomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'demo_multiple_fields_1_model'

    def ready(self):
        import demo_multiple_fields_1_model.receivers  # noqa
