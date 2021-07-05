from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_image_model():
    from django.apps import django_apps
    try:
        return django_apps.get_model(settings.DJANGO_GALLERY_APP["IMAGE_MODEL"], require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("DJANGO_GALLERY_APP['IMAGE_MODEL'] must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "IMAGE_MODEL refers to model '%s' that has not been installed"
            % settings.DJANGO_GALLERY_APP['IMAGE_MODEL']
        )
