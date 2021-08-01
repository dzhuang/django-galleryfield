from django.utils.deconstruct import deconstructible
from django.db import models
from django.utils.translation import gettext_lazy as _, ngettext_lazy
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.db.models.query_utils import DeferredAttribute
from django.db.models import Case, Value, When, IntegerField

from gallery import conf, defaults as gallery_widget_defaults
from gallery.widgets import GalleryWidget
from gallery.utils import get_or_check_image_field, apps


@deconstructible
class MaxNumberOfImageValidator(BaseValidator):
    message = ngettext_lazy(
        'Number of images exceeded, only %(limit_value)d allowed',
        'Number of images exceeded, only %(limit_value)d allowed',
        'limit_value')
    code = 'max_number_of_images'

    def compare(self, a, b):
        return a > b

    def clean(self, x):
        return len(x)


class GalleryDescriptor(DeferredAttribute):
    """
    Used django.db.models.fields.files.FileDescriptor as an example.
    """

    def __set__(self, instance, value):
        instance.__dict__[self.field.attname] = value

    def __get__(self, instance, cls=None):
        image_list = super().__get__(instance, cls)

        if (isinstance(image_list, list)
                and not isinstance(image_list, GalleryImageList)):
            attr = self.field.attr_class(instance, self.field, image_list)
            instance.__dict__[self.field.name] = attr

        return instance.__dict__[self.field.name]


class GalleryImageList(list):
    def __init__(self, instance, field, field_value):
        super().__init__(field_value)
        self._field = field
        self.instance = instance
        self._value = field_value

    @property
    def objects(self):
        model = apps.get_model(self._field.target_model)

        # Preserving the order of image using id__in=pks
        # https://stackoverflow.com/a/37146498/3437454
        cases = [When(id=x, then=Value(i)) for i, x in enumerate(self._value)]
        case = Case(*cases, output_field=IntegerField())
        filter_kwargs = {"id__in": self._value}
        queryset = model.objects.filter(**filter_kwargs)
        queryset = queryset.annotate(_order=case).order_by('_order')
        return queryset


class GalleryField(models.JSONField):
    description = _('An array JSON object as attributes of (multiple) images')
    default_error_messages = {
        'invalid': _('Value must be valid JSON.'),
    }
    attr_class = GalleryImageList
    descriptor_class = GalleryDescriptor

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)
        setattr(cls, self.attname, self.descriptor_class(self))

    def get_internal_type(self):
        return 'JSONField'

    def __init__(self, target_model=None, *args, **kwargs):
        self._init_target_model = self.target_model = target_model
        if target_model is None:
            self.target_model = gallery_widget_defaults.DEFAULT_TARGET_IMAGE_MODEL

        self.target_model_image_field = (
            self._get_image_field_or_test(is_checking=False))

        super().__init__(*args, **kwargs)

    def _get_image_field_or_test(self, is_checking=False):
        return get_or_check_image_field(
            target_app_model_str=self._init_target_model,
            check_id_prefix="gallery_field",
            obj=self, is_checking=is_checking,
            log_if_using_default_in_checks=True)

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        errors.extend(self._check_target_model())
        return errors

    def _check_target_model(self):
        return self._get_image_field_or_test(is_checking=True)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['target_model'] = self.target_model
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        _defaults = ({
            "required": True,

            # The following 2 are used to validate GalleryWidget settings
            # see GalleryWidget.defaults_checks()
            "image_model": self.target_model,
            "model_field": str(self)
        })
        _defaults.update(kwargs)
        formfield = super().formfield(**{
            'form_class': GalleryFormField,
            **_defaults,
        })
        return formfield


class GalleryFormField(forms.JSONField):
    default_error_messages = {
        'required': _("The submitted file is empty."),
        'invalid': _("The submitted images are invalid."),
    }

    def __init__(self, max_number_of_images=None, **kwargs):
        self.image_model = kwargs.pop("image_model", conf.DEFAULT_TARGET_IMAGE_MODEL)
        widget_belong = kwargs.pop("model_field", None)

        if widget_belong is None:
            # No model field is used
            widget_belong = str(self)
        self.widget_belong = widget_belong
        self._max_number_of_images = max_number_of_images
        super().__init__(**kwargs)

        self._widget.image_model = self.image_model
        self._widget.widget_belong = widget_belong

    _widget = GalleryWidget

    @property
    def widget(self):
        return self._widget

    @widget.setter
    def widget(self, value):
        setattr(value, "max_number_of_images", self.max_number_of_images)
        setattr(value, "image_model", self.image_model)
        setattr(value, "widget_belong", self.widget_belong)

        # Re-initialize the widget
        # todo: test widget instance change in form
        value.is_localized = bool(self.localize)
        value.is_required = self.required
        extra_attrs = self.widget_attrs(value) or {}
        value.attrs.update(extra_attrs)
        self._widget = value

        assert self.widget.max_number_of_images == self.max_number_of_images

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
        self._widget.max_number_of_images = value

        if value:
            self.validators.append(
                MaxNumberOfImageValidator(int(value)))

    def widget_attrs(self, widget):
        # If BootStrap is loaded, "hiddeninput" is added by BootStrap.
        # However, we need that css class to check changes of the form,
        # so we added it manually.
        return {
            "class": " ".join(
                [conf.FILES_FIELD_CLASS_NAME, "hiddeninput"])
        }

    def to_python(self, value):
        converted = super().to_python(value)

        if converted in self.empty_values:
            return converted

        # Make sure the json is a list of pks
        if not isinstance(converted, list):
            raise ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': converted},
            )

        for _pk in converted:
            if not str(_pk).isdigit():
                raise ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': converted},
                )

        if self.image_model is None:
            return converted

        # Make sure all pks exists
        image_model = apps.get_model(self.image_model)
        if (image_model.objects.filter(
                pk__in=list(map(int, converted))).count()
                != len(converted)):
            converted_copy = converted[:]
            converted = []
            for pk in converted_copy:
                if image_model.objects.filter(pk=pk).count():
                    converted.append(pk)

        return converted
