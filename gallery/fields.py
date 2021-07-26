import json
from copy import deepcopy

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from django.core.exceptions import ValidationError

from .controller import manage_images
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

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)
        receiver(post_save, sender=cls)(manage_images)
        # todo GalleryDescriptor
        # setattr(cls, self.name, GalleryDescriptor(self))

    def save_form_data(self, instance, data):
        # Save old data to know which images are deleted.
        # We don't know yet if the form will really be saved.

        old_data = getattr(instance, self.name)
        setattr(instance, conf.OLD_VALUE_STR % self.name, old_data)
        setattr(instance, conf.DELETED_VALUE_STR % self.name, data.deleted_files)

        super(GalleryField, self).save_form_data(instance, data)

    def formfield(self, **kwargs):
        defaults = ({"required": True})
        defaults.update(kwargs)
        return super(models.JSONField, self).formfield(**{
            'form_class': GalleryFormField,
            **defaults,
        })


class ImageJsonFormField(forms.JSONField):
    default_error_messages = {
        'required': _("The submitted file is empty."),
        'invalid': _("The submitted images are invalid."),
    }

    def __init__(self, max_number_of_images=None, **kwargs):
        self.max_number_of_images = max_number_of_images
        super().__init__(encoder=None, decoder=None, **kwargs)

    def clean(self, value):
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

        # Make sure the json is a list of dicts, each of which
        # must has least has a 'url' key.
        if not isinstance(cleaned_data_copy, list):
            raise ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': cleaned_data},
            )
        for image_dict in cleaned_data_copy:
            if not isinstance(image_dict, dict) or "url" not in image_dict:
                raise ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': cleaned_data},
                )

        if self.max_number_of_images is not None:
            if len(cleaned_data_copy) > self.max_number_of_images:
                raise ValidationError(
                    _("Number of images exceeded, only %(maxNumberOfFiles)s allowed")
                    % {"maxNumberOfFiles": self.max_number_of_images}
                )
        return cleaned_data


class GalleryFormField(forms.MultiValueField):
    default_error_messages = {
        'required': _("The submitted file is empty."),
        'invalid': _("The submitted images are invalid."),
    }

    widget = GalleryWidget

    def __init__(self, max_number_of_images=None, **kwargs):
        self._required = kwargs.get("required", True)
        self._max_number_of_images = max_number_of_images
        kwargs.update(
            {
                'fields': (
                    ImageJsonFormField(required=self._required,
                                       max_number_of_images=max_number_of_images),
                    ImageJsonFormField(required=False))
            }
        )
        super(GalleryFormField, self).__init__(require_all_fields=False, **kwargs)
        self.widget.max_number_of_images = self.max_number_of_images\
            = max_number_of_images

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
        self.fields[0].max_number_of_images = value
        self.widget.max_number_of_images = value

    @property
    def required(self):
        return self._required

    @required.setter
    def required(self, value):
        # In this way, changes in field required will be synced to
        # required attributes of subfield(fields[0])
        assert isinstance(value, bool)
        self._required = value

        # Prevent failing in super().__init__
        try:
            self.fields[0].required = value
        except AttributeError:
            pass

    def compress(self, data_list):
        if not data_list:
            data_list = ['', '']

        if data_list[0] is None:
            data_list[0] = ''

        files = UnicodeWithAttr(json.dumps(data_list[0]))
        setattr(files, "deleted_files", data_list[1])
        return files

    def clean(self, value):
        clean_data = []
        errors = []
        if self.disabled and not isinstance(value, list):
            value = self.widget.decompress(value)
        if not value or isinstance(value, (list, tuple)):
            # We don't save deleted_files in db, so no need to check value[1]
            if not value or value[0] in self.empty_values:
                if self.required:
                    raise ValidationError(
                        self.error_messages['required'], code='required')
                else:
                    if not value:
                        return self.compress([])

        else:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        for i, field in enumerate(self.fields):
            try:
                field_value = value[i]
            except IndexError:
                field_value = None

            try:
                clean_data.append(field.clean(field_value))
            except ValidationError as e:
                # Collect all validation errors in a single list, which we'll
                # raise at the end of clean(), rather than raising a single
                # exception for the first error we encounter. Skip duplicates.
                errors.extend(m for m in e.error_list if m not in errors)
        if errors:
            raise ValidationError(errors)

        out = self.compress(clean_data)
        self.validate(out)
        self.run_validators(out)

        return out
