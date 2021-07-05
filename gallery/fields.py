from django.db import models
from django.utils.translation import gettext_lazy as _


class ImagesField(models.JSONField):
    # empty_strings_allowed = False
    description = _('An array JSON object as attributes of (multiple) images')
    default_error_messages = {
        'invalid': _('Value must be valid JSON.'),
    }

    def __init__(
        self, verbose_name=None, name=None, encoder=None, decoder=None,
        **kwargs,
    ):
        kwargs.update({"default": list})
        super().__init__(verbose_name, name, encoder, decoder, **kwargs)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        # todo: valide format
