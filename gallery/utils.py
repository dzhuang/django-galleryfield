import logging
logger = logging.getLogger('django-gallery-widget')

try:
    from django.apps import apps  # noqa
except ImportError:
    from django.apps import django_apps as apps  # noqa


def convert_dict_to_plain_text(d, indent=4):
    result = []
    for k, v in d.items():
        if v is not None:
            result.append(" " * indent + "%s: %s," % (k, str(v)))
    return "\n".join(result)
