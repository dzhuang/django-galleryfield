from django.apps import AppConfig


class GalleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'galleryfield'

    def ready(self):
        from .checks import register_galleryfield_settings_checks
        register_galleryfield_settings_checks()
