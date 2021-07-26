import json

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
        kwargs.update({"required": True})
        return super(models.JSONField, self).formfield(**{
            'form_class': GalleryFormField,
            **kwargs,
        })


class GalleryFormField(forms.MultiValueField):
    default_error_messages = {
        'required': _("The submitted file is empty."),
        'invalid': _("The submitted images are invalid."),
    }

    widget = GalleryWidget

    def __init__(self, max_length=None, encoder=None, decoder=None, **kwargs):
        """
        Note: Here we are actually extending forms.JsonField, so encoder and
        decoder are needed
        """

        required = kwargs.get("required", True)
        self.decoder = decoder
        self.encoder = encoder

        kwargs.update(
            {
                'fields': (
                    forms.JSONField(required=required),
                    forms.JSONField(required=False))
            }
        )
        super(GalleryFormField, self).__init__(require_all_fields=False, **kwargs)

    def compress(self, data_list):
        if not data_list:
            data_list = ['', '']

        files = UnicodeWithAttr(json.dumps(data_list[0]))
        setattr(files, "deleted_files", data_list[1])
        return files

    def _validate_json_list_of_image_dict(self, json_list_str):
        try:
            assert isinstance(json_list_str, str)
            images_list = json.loads(json_list_str)
        except (AssertionError, json.JSONDecodeError):
            raise ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': json_list_str},
            )
        else:
            # Make sure the json is a list of dicts, each of which
            # must has least has a 'url' key.
            if not isinstance(images_list, list):
                raise ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': json_list_str},
                )
            for image_dict in images_list:
                if not isinstance(image_dict, dict) or "url" not in image_dict:
                    raise ValidationError(
                        self.error_messages['invalid'],
                        code='invalid',
                        params={'value': json_list_str},
                    )

    def _pre_compress_value_list_validate(self, value):
        assert isinstance(value, (list, tuple))
        for v in value:
            if v in self.empty_values:
                continue
            self._validate_json_list_of_image_dict(v)

    def _post_clean_field_value_validate(self, value):
        if value in self.empty_values:
            return
        self._validate_json_list_of_image_dict(value)

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
                        # This happens when not required, files value is empty and
                        # deleted files value is not necessary empty.
                        self._pre_compress_value_list_validate(value)
                        clean_data = self.compress(value)
                        self.validate(clean_data)
                        return clean_data
        else:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        for i, field in enumerate(self.fields):
            try:
                field_value = value[i]
            except IndexError:
                field_value = None

            try:
                clean_data.append(field.clean(field_value))
                self._post_clean_field_value_validate(field_value)
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
