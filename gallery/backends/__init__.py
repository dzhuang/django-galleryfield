from django.utils.module_loading import import_string
from gallery.conf import DEFAULT_BACKEND


def get_backend():
    return import_string(DEFAULT_BACKEND)
