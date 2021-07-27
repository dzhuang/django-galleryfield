import json
from copy import deepcopy

from django.db import models
from django.utils.translation import gettext_lazy as _
from django import forms
from django.core.exceptions import ValidationError

from . import conf
from .widgets import GalleryWidget


class UnicodeWithAttr(str):
    """
    This is used to store deleted files, which are then to be
    handled when calling `save_form_data`, through
    """
    deleted_files = None


class GalleryField(models.JSONField):
    description = _('An array JSON object as attributes of (multiple) images')
    default_error_messages = {
        'invalid': _('Value must be valid JSON.'),
    }

    def formfield(self, **kwargs):
        defaults = ({"required": True})
        defaults.update(kwargs)
        return super(models.JSONField, self).formfield(**{
            'form_class': GalleryFormField,
            **defaults,
        })


class GalleryFormField(forms.JSONField):
    default_error_messages = {
        'required': _("The submitted file is empty."),
        'invalid': _("The submitted images are invalid."),
    }

    def __init__(self, max_number_of_images=None, **kwargs):
        self.max_number_of_images = max_number_of_images
        super().__init__(encoder=None, decoder=None, **kwargs)

        self.widget.max_number_of_images = self.max_number_of_images\
            = max_number_of_images

    widget = GalleryWidget

    def widget_attrs(self, widget):
        # If BootStrap is loaded, "hiddeninput" is added by BootStrap.
        # However, we need that css class to check changes of the form,
        # so we added it manually.
        return {
            "class": " ".join(
                [conf.FILES_FIELD_CLASS_NAME, "hiddeninput"])
        }

    def clean(self, value):
        print("clean!!!")
        cleaned_data = super().clean(value)

        if cleaned_data in self.empty_values:
            return cleaned_data

        if isinstance(cleaned_data, str):
            try:
                cleaned_data_copy = json.loads(cleaned_data, cls=self.decoder)
            except json.JSONDecodeError:
                raise ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': cleaned_data},
                )
        else:
            cleaned_data_copy = deepcopy(cleaned_data)

        # Make sure the json is a list of pks
        if not isinstance(cleaned_data_copy, list):
            raise ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': cleaned_data},
            )
        for _pk in cleaned_data_copy:
            if not str(_pk).isdigit():
                raise ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': cleaned_data},
                )

        if self.max_number_of_images:
            if len(cleaned_data_copy) > self.max_number_of_images:
                raise ValidationError(
                    _("Number of images exceeded, only %(maxNumberOfFiles)s allowed")
                    % {"maxNumberOfFiles": self.max_number_of_images}
                )
        return cleaned_data

    @property
    def max_number_of_images(self):
        return self._max_number_of_images

    @max_number_of_images.setter
    def max_number_of_images(self, value):
        if value is not None:
            if not str(value).isdigit():
                raise TypeError(
                    "'max_number_of_images' expects a positive integer, "
                    "got %s." % str(value))
            value = int(value)
        self._max_number_of_images = value
        self.widget.max_number_of_images = value
