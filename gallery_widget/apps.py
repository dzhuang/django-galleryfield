from django.apps import AppConfig


class GalleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gallery_widget'

    def ready(self):
        from .checks import register_gallery_widget_settings_checks
        register_gallery_widget_settings_checks()
