import logging

from django.core.checks import Critical, Info
from django.core.exceptions import (
    ImproperlyConfigured, FieldDoesNotExist, AppRegistryNotReady)
from django.db.models import ImageField

from gallery import defaults

try:
    from django.apps import apps  # noqa pragma: no cover
except ImportError:  # noqa pragma: no cover
    from django.apps import django_apps as apps  # noqa pragma: no cover


logger = logging.getLogger('django-gallery-widget')


class DJGalleryCriticalCheckMessage(Critical):
    def __init__(self, *args, **kwargs):
        super(DJGalleryCriticalCheckMessage, self).__init__(*args, **kwargs)
        self.obj = self.obj or ImproperlyConfigured.__name__


INSTANCE_ERROR_PATTERN = "%(location)s must be an instance of %(types)s."
GENERIC_ERROR_PATTERN = "Error in %(location)s: %(error_type)s: %(error_str)s"
REQUIRED_CONF_ERROR_PATTERN = (
    "You must configure %(location)s for RELATE to run properly.")


def convert_dict_to_plain_text(d, indent=4):
    result = []
    for k, v in d.items():
        if v is not None:
            result.append(" " * indent + "%s: %s," % (k, str(v)))
    return "\n".join(result)


def get_or_check_image_field(
        target_app_model_str, check_id_prefix, location=None, obj=None,
        is_checking=False, log_if_using_default_in_checks=False):
    assert location or obj
    errors = []
    target_model = None
    will_proceed_checking_target_model_image_fields = True
    if target_app_model_str is not None:
        if not isinstance(target_app_model_str, str):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": location or str(obj),
                        "types": "str"}),
                id="%s.E001" % check_id_prefix,
                obj=obj
            ))
            will_proceed_checking_target_model_image_fields = False
        else:
            try:
                target_model = apps.get_model(target_app_model_str)
            except Exception as e:
                if isinstance(e, AppRegistryNotReady):
                    if not is_checking:
                        return None
                if not is_checking:
                    return None
                errors.append(DJGalleryCriticalCheckMessage(
                    msg=(GENERIC_ERROR_PATTERN
                         % {"location": location or str(obj),
                            "error_type": type(e).__name__,
                            "error_str": str(e)}
                         + "\n See "
                           "https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.get_model"  # noqa
                           " for more information."
                         ),
                    id="%s.E002" % check_id_prefix,
                    obj=obj
                ))
                will_proceed_checking_target_model_image_fields = False

    if will_proceed_checking_target_model_image_fields:
        if target_model is None:
            target_app_model_str = defaults.DEFAULT_TARGET_IMAGE_MODEL
            try:
                target_model = apps.get_model(target_app_model_str)
            except AppRegistryNotReady:
                assert not is_checking
                return None
            else:
                if log_if_using_default_in_checks:
                    errors.append(Info(
                        msg=('"target_model" is set to None, '
                             '"%(default)s" is used as default.'
                             % {"default": defaults.DEFAULT_TARGET_IMAGE_MODEL}
                             ),
                        id="%s.I001" % check_id_prefix,
                        obj=obj
                    ))

        get_image_field_class_method = None
        get_image_field_class_method_raised_error = False
        try:
            image_field = (
                target_model._meta.get_field(
                    defaults.DEFAULT_TARGET_IMAGE_FIELD_NAME))
            if type(image_field) is not ImageField:
                raise FieldDoesNotExist()
        except FieldDoesNotExist:
            image_field = None
            get_image_field_class_method = getattr(target_model,
                                                   "get_image_field", None)
            if get_image_field_class_method is not None:
                if callable(get_image_field_class_method):
                    try:
                        image_field = get_image_field_class_method()
                    except Exception as e:
                        if not is_checking:
                            return None
                        errors.append(Critical(
                            msg=('Error in %(location)s: model %(model)s defined '
                                 '"get_image_field" method failed with'
                                 ' %(exception)s: %(str_e)s'
                                 % {"location": location or str(obj),
                                    "model": target_app_model_str,
                                    "exception": type(e).__name__,
                                    "str_e": str(e)
                                    }),
                            id="%s.E003" % check_id_prefix,
                            obj=obj
                        ))
                        get_image_field_class_method_raised_error = True
                else:
                    image_field = get_image_field_class_method

        if image_field is not None:
            if type(image_field) is not ImageField:
                image_field = None

        if image_field is None:
            if not is_checking:
                return None
            if get_image_field_class_method is None:
                errors.append(Critical(
                    msg=('Error in %(location)s: model %(model)s must '
                         'either have a field named "image" '
                         'or has a classmethod named "get_image_field", '
                         'which returns the image field of the model'
                         % {"location": location or str(obj),
                            "model": target_app_model_str
                            }),
                    id="%s.E004" % check_id_prefix,
                    obj=obj
                ))
            elif not get_image_field_class_method_raised_error:
                errors.append(Critical(
                    msg=('Error in %(location)s: model %(model)s defined '
                         '"get_image_field" class method '
                         'did not return a ImageField type'
                         % {"location": location or str(obj),
                            "model": target_app_model_str
                            }),
                    id="%s.E005" % check_id_prefix,
                    obj=obj
                ))
        else:
            if not is_checking:
                return image_field

    return errors
