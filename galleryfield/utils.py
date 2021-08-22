import logging

from django.apps import apps
from django.core.checks import Critical, Info
from django.core.exceptions import (AppRegistryNotReady, FieldDoesNotExist,
                                    ImproperlyConfigured)
from django.db.models import ImageField
from django.urls import (NoReverseMatch, Resolver404, resolve, reverse,
                         reverse_lazy)

from galleryfield import defaults

logger = logging.getLogger('django-galleryfield')


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
            if v in [True, False]:
                v = str(v).lower()
            result.append(" " * indent + "%s: %s," % (k, str(v)))
    return "\n".join(result)


def get_or_check_image_field(obj, target_model, check_id_prefix, is_checking=False):
    """Get the image field from target image model, or check if the params will work
    in the model during model.check().

    :param target_model: a string or ``None``. If ``None``,
           ``defaults.DEFAULT_TARGET_IMAGE_MODEL`` will be used.
    :type target_model: str
    :param check_id_prefix: The function will be used in model checks and formfield
           checks . They will use different check message id.
    :param obj: Where the check error is detected, used for model checks.
    :param is_checking: whether this function is used in checks.
    :return: when ``is_checking`` is ``False``, we were getting the image field from
      the target image model. if any errors this will return ``None``, and the errors
      will be raised in model checks, i.e., when ``is_checking`` is ``True``.
    """

    errors = []
    target_model_klass = None
    will_proceed_checking_target_model_image_fields = True
    if target_model is not None:
        if not isinstance(target_model, str):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": str(obj),
                        "types": "str"}),
                id="%s.E001" % check_id_prefix,
                obj=obj
            ))
            will_proceed_checking_target_model_image_fields = False
        else:
            try:
                target_model_klass = apps.get_model(target_model)
            except AppRegistryNotReady:
                # Preventing from failing in field initialization
                # We will raise that in field check
                assert not is_checking
                return None
            except Exception as e:
                if not is_checking:
                    return None

                # todo: add doc ref in the error
                errors.append(DJGalleryCriticalCheckMessage(
                    msg=(GENERIC_ERROR_PATTERN
                         % {"location": str(obj),
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
        if target_model_klass is None:
            target_model = defaults.DEFAULT_TARGET_IMAGE_MODEL
            try:
                target_model_klass = apps.get_model(target_model)
            except AppRegistryNotReady:
                assert not is_checking
                # Preventing from failing in field initialization
                # We will raise that in field check
                return None
            # Here we assume defaults.DEFAULT_TARGET_IMAGE_MODEL will always work
            else:
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
                target_model_klass._meta.get_field(
                    defaults.DEFAULT_TARGET_IMAGE_FIELD_NAME))
            if type(image_field) is not ImageField:
                raise FieldDoesNotExist()
        except FieldDoesNotExist:
            image_field = None
            get_image_field_class_method = (
                getattr(target_model_klass, "get_image_field", None))
            if get_image_field_class_method is not None:
                if callable(get_image_field_class_method):
                    try:
                        image_field = get_image_field_class_method()
                    except Exception as e:
                        if not is_checking:
                            # Preventing from failing in field initialization
                            # We will raise that in field check
                            return None
                        errors.append(Critical(
                            msg=('Error in %(location)s: model %(model)s defined '
                                 '"get_image_field" method failed with'
                                 ' %(exception)s: %(str_e)s'
                                 % {"location": str(obj),
                                    "model": target_model,
                                    "exception": type(e).__name__,
                                    "str_e": str(e)
                                    }),
                            id="%s.E003" % check_id_prefix,
                            obj=obj
                        ))
                        get_image_field_class_method_raised_error = True

        if image_field is not None:
            if type(image_field) is not ImageField:
                image_field = None

        if image_field is None:
            if not is_checking:
                # Preventing from failing in field initialization
                # We will raise that in field check
                return None
            if get_image_field_class_method is None:
                errors.append(Critical(
                    msg=('Error in %(location)s: model %(model)s must '
                         'either have a field named "image" '
                         'or has a classmethod named "get_image_field", '
                         'which returns the image field of the model'
                         % {"location": str(obj),
                            "model": target_model
                            }),
                    id="%s.E004" % check_id_prefix,
                    obj=obj
                ))
            elif not get_image_field_class_method_raised_error:
                errors.append(Critical(
                    msg=('Error in %(location)s: model %(model)s defined '
                         '"get_image_field" class method '
                         'did not return a ImageField type'
                         % {"location": str(obj),
                            "model": target_model
                            }),
                    id="%s.E005" % check_id_prefix,
                    obj=obj
                ))
        else:
            if not is_checking:
                return image_field

    return errors


def get_url_from_str(url_str, require_urlconf_ready=False):
    """

    :param url_str:
    :param require_urlconf_ready: During the system loading stage,
     We had to use ``reverse_lazy``, or else it will result in
     circular import.
     Ref: https://docs.djangoproject.com/en/dev/ref/urlresolvers/#reverse-lazy
     And that means wen url_str will only be evaluated and validate
     before requests.
    :return: an URL string or a lazy reverse object
    """
    if not url_str:
        return None
    try:
        resolve(url_str)
    except Resolver404:
        if not require_urlconf_ready:
            return reverse_lazy(url_str)
        try:
            return reverse(url_str)
        except NoReverseMatch:
            raise ImproperlyConfigured(
                "'%s' is neither a valid URL nor a valid URL name" % url_str)
    return url_str


class InvalidThumbnailFormat(ValueError):
    pass


def get_formatted_thumbnail_size(thumbnail_size, name="thumbnail_size"):
    if not thumbnail_size:
        thumbnail_size = defaults.DEFAULT_THUMBNAIL_SIZE

    def get_thumb_size_from_iterator(size_iter):
        if not 0 < len(size_iter) <= 2:
            raise InvalidThumbnailFormat()
        for _item in size_iter:
            if not str(_item).isdigit():
                raise InvalidThumbnailFormat(str(_item))
        if len(size_iter) == 1:
            size_iter = size_iter * 2
        return "x".join(list(map(str, size_iter)))

    if not isinstance(thumbnail_size, (list, tuple)):
        thumbnail_size = str(thumbnail_size).strip()
        if not thumbnail_size:
            raise ValueError(
                "'%s' can't be an empty string" % name)
        thumbnail_size = [s.strip() for s in thumbnail_size.lower().split("x")]

    return get_thumb_size_from_iterator(thumbnail_size)
