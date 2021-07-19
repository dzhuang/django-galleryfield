import json

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms

from .controller import manage_images
from .widgets import GalleryWidget
from . import conf


class UnicodeWithAttr(str):
    """
    This is used to store deleted files and moved_files, which are then to be
    handled when calling `save_form_data`, through
    """
    deleted_files = None
    moved_files = None


def save_all_data(self, instance, data):
    # Save old data to know which images are deleted.
    # We don't know yet if the form will really be saved.

    old_data = getattr(instance, self.name)
    setattr(instance, conf.OLD_VALUE_STR % self.name, old_data)
    setattr(instance, conf.DELETED_VALUE_STR % self.name, data.deleted_files)
    setattr(instance, conf.MOVED_VALUE_STR % self.name, data.moved_files)


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
        save_all_data(self, instance, data)
        super(GalleryField, self).save_form_data(instance, data)

    def formfield(self, **kwargs):
        return super(models.JSONField, self).formfield(**{
            'form_class': GalleryFormField,
            **kwargs,
        })

    def _formfield_defaults(self, default_widget=None, widget=None, required=True, **kwargs):
        from .widgets import GalleryWidget
        if not isinstance(widget, GalleryWidget):
            widget = default_widget
        defaults = {
            'form_class': self._get_form_class(),
            'fields': (
                forms.JSONField(required=required),
                forms.JSONField(required=False),
                forms.JSONField(required=False),),
            'widget': widget,

            # This line is required for GalleryWidget to set correct required subwidget
            'required': required
        }
        defaults.update(kwargs)

        return defaults

    @staticmethod
    def _get_form_class():
        return GalleryFormField


class GalleryFormField(forms.MultiValueField):
    default_error_messages = {
        'incomplete': _("The submitted file is empty."),
        'required': _("The submitted file is empty."),
    }

    def __init__(self, max_length=None, encoder=None, decoder=None, **kwargs):
        """
        Note: Here we are actually extending forms.JsonField, so encoder and
        decoder are needed
        """
        from .widgets import GalleryWidget

        kwargs.update(
            {
                "widget": GalleryWidget(),
                'fields': (
                   forms.JSONField(required=kwargs.get("required"),
                                   encoder=encoder, decoder=decoder),
                   forms.JSONField(required=False, encoder=encoder,
                                   decoder=decoder),
                   forms.JSONField(required=False, encoder=encoder,
                                   decoder=decoder), ),
                "require_all_fields": False
            }
        )
        super(GalleryFormField, self).__init__(**kwargs)

    def compress(self, data_list):
        if not data_list:
            data_list = ['', '', '']

        files = UnicodeWithAttr(json.dumps(data_list[0]))
        assert data_list[2] is None or len(data_list[2]) == 0, data_list
        setattr(files, "deleted_files", data_list[1])
        setattr(files, "moved_files", data_list[2])
        return files
