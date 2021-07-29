from django.conf import settings
from django.core.checks import Critical, register
from django.core.exceptions import ImproperlyConfigured, FieldDoesNotExist

from django.urls import reverse
from django.db.models import ImageField

from . import conf as app_conf
from . import defaults
from .utils import apps


REQUIRED_CONF_ERROR_PATTERN = (
    "You must configure %(location)s for RELATE to run properly.")
INSTANCE_ERROR_PATTERN = "%(location)s must be an instance of %(types)s."
GENERIC_ERROR_PATTERN = "Error in %(location)s: %(error_type)s: %(error_str)s"

DJANGO_GALLERY_WIDGET_CONFIG = "DJANGO_GALLERY_WIDGET_CONFIG"
DEFAULT_URLS = "default_urls"
UPLOAD_HANDLER_URL_NAME = "upload_handler_url_name"
FETCH_URL_NAME = "fetch_url_name"
CROP_URL_NAME = "crop_url_name"

DEFAULT_TARGET_IMAGE_MODEL = "target_image_model"

ASSETS = "assets"
BOOTSTRAP_JS_PATH = "bootstrap_js_path"
BOOTSTRAP_CSS_PATH = "bootstrap_css_path"
JQUERY_JS_PATH = "jquery_js_path"
EXTRA_JS = "extra_js"
EXTRA_CSS = "extra_css"

THUMBNAILS = "thumbnails"
THUMBNAIL_SIZE = "size"
THUMBNAIL_QUALITY = "quality"

WIDGET_HIDDEN_INPUT_CSS_CLASS = "widget_hidden_input_css_class"

PROMPT_ALERT_IF_CHANGED_ON_WINDOW_RELOAD = (
    "prompt_alert_if_changed_on_window_reload")


def register_gallery_widget_settings_checks():
    register(check_settings, "django_gallery_widget_checks")


class DJGalleryCriticalCheckMessage(Critical):
    def __init__(self, *args, **kwargs):
        super(DJGalleryCriticalCheckMessage, self).__init__(*args, **kwargs)
        self.obj = self.obj or ImproperlyConfigured.__name__


def check_settings(app_configs, **kwargs):
    errors = []

    conf = getattr(settings, "DJANGO_GALLERY_WIDGET_CONFIG", None)
    if conf is None:
        return errors

    if not isinstance(conf, dict):
        errors.append(DJGalleryCriticalCheckMessage(
            msg=(INSTANCE_ERROR_PATTERN
                 % {"location": DJANGO_GALLERY_WIDGET_CONFIG, "types": "dict"}),
            id="django-gallery-widget.E001"
        ))
        return errors

    default_urls = conf.get(DEFAULT_URLS, None)
    if default_urls is not None:
        if not isinstance(default_urls, dict):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": "'%s' in '%s'" % (
                            DEFAULT_URLS, DJANGO_GALLERY_WIDGET_CONFIG),
                        "types": "dict"}),
                id="django-gallery-widget-default_urls.E001"
            ))
        else:
            upload_handler_url_name = default_urls.get(UPLOAD_HANDLER_URL_NAME,
                                                       None)
            if upload_handler_url_name is not None:
                if not isinstance(upload_handler_url_name, str):
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(INSTANCE_ERROR_PATTERN
                             % {"location": "'%s' in '%s' in '%s'" % (
                                    UPLOAD_HANDLER_URL_NAME, DEFAULT_URLS,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "types": "str"}),
                        id="django-gallery-widget-default_urls.E002"
                    ))
                else:
                    try:
                        reverse(upload_handler_url_name)
                    except Exception as e:
                        errors.append(DJGalleryCriticalCheckMessage(
                            msg=(GENERIC_ERROR_PATTERN
                                 % {"location": "'%s' in '%s' in '%s'" % (
                                        UPLOAD_HANDLER_URL_NAME, DEFAULT_URLS,
                                        DJANGO_GALLERY_WIDGET_CONFIG),
                                    "error_type": type(e).__name__,
                                    "error_str": str(e)}),
                            id="django-gallery-widget-default_urls.E003"
                        ))

            crop_url_name = default_urls.get(CROP_URL_NAME, None)
            if crop_url_name is not None:
                if not isinstance(crop_url_name, str):
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(INSTANCE_ERROR_PATTERN
                             % {"location": "'%s' in '%s' in '%s'" % (
                                    CROP_URL_NAME, DEFAULT_URLS,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "types": "str"}),
                        id="django-gallery-widget-default_urls.E004"
                    ))
                else:
                    try:
                        reverse(crop_url_name)
                    except Exception as e:
                        errors.append(DJGalleryCriticalCheckMessage(
                            msg=(GENERIC_ERROR_PATTERN
                                 % {"location": "'%s' in '%s' in '%s'" % (
                                        CROP_URL_NAME, DEFAULT_URLS,
                                        DJANGO_GALLERY_WIDGET_CONFIG),
                                    "error_type": type(e).__name__,
                                    "error_str": str(e)}),
                            id="django-gallery-widget-default_urls.E005"
                        ))

            fetch_url_name = default_urls.get(FETCH_URL_NAME, None)
            if fetch_url_name is not None:
                if not isinstance(fetch_url_name, str):
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(INSTANCE_ERROR_PATTERN
                             % {"location": "'%s' in '%s' in '%s'" % (
                                    FETCH_URL_NAME, DEFAULT_URLS,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "types": "str"}),
                        id="django-gallery-widget-default_urls.E006"
                    ))
                else:
                    try:
                        reverse(fetch_url_name)
                    except Exception as e:
                        errors.append(DJGalleryCriticalCheckMessage(
                            msg=(GENERIC_ERROR_PATTERN
                                 % {"location": "'%s' in '%s' in '%s'" % (
                                        FETCH_URL_NAME, DEFAULT_URLS,
                                        DJANGO_GALLERY_WIDGET_CONFIG),
                                    "error_type": type(e).__name__,
                                    "error_str": str(e)}),
                            id="django-gallery-widget-default_urls.E007"
                        ))

    default_target_image_model = conf.get(
        DEFAULT_TARGET_IMAGE_MODEL, None)
    target_model = None
    will_proceed_checking_target_model_image_fields = True
    if default_target_image_model is not None:
        if not isinstance(default_target_image_model, str):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": "'%s' in '%s'" % (
                            DEFAULT_TARGET_IMAGE_MODEL,
                            DJANGO_GALLERY_WIDGET_CONFIG),
                        "types": "str"}),
                id="django-gallery-widget-default_image_model.E001"
            ))
            will_proceed_checking_target_model_image_fields = False
        else:
            try:
                target_model = apps.get_model(default_target_image_model)
            except Exception as e:
                errors.append(DJGalleryCriticalCheckMessage(
                    msg=(GENERIC_ERROR_PATTERN
                         % {"location": "'%s' in '%s'" % (
                                DEFAULT_TARGET_IMAGE_MODEL,
                                DJANGO_GALLERY_WIDGET_CONFIG),
                            "error_type": type(e).__name__,
                            "error_str": str(e)}
                         + "\n See "
                           "https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.get_model"  # noqa
                           " for more information."
                         ),
                    id="django-gallery-widget-default_image_model.E002"
                ))
                will_proceed_checking_target_model_image_fields = False

        if will_proceed_checking_target_model_image_fields:
            if target_model is None:
                default_target_image_model = defaults.DEFAULT_TARGET_IMAGE_MODEL
                target_model = apps.get_model(default_target_image_model)

            get_image_field_class_method = None
            try:
                image_field = (
                    target_model._meta.get_field(
                        defaults.DEFAULT_TARGET_IMAGE_FIELD_NAME))
            except FieldDoesNotExist:
                image_field = None
                get_image_field_class_method = getattr(target_model,
                                                       "get_image_field", None)
                if get_image_field_class_method is not None:
                    get_image_field_method_valid = True
                    if callable(get_image_field_class_method):
                        try:
                            image_field = get_image_field_class_method()
                        except TypeError:
                            get_image_field_method_valid = False

                    if not get_image_field_method_valid:
                        errors.append(Critical(
                            msg=('Error in %(location)s: model %(model)s defined '
                                 '"get_image_field" method is not a classmethod'
                                 % {"location": "'%s' in '%s'" % (
                                        DEFAULT_TARGET_IMAGE_MODEL,
                                        DJANGO_GALLERY_WIDGET_CONFIG),
                                    "model": default_target_image_model
                                 }),
                            id="django-gallery-widget-default_image_model.E003"
                        ))

            if image_field is not None:
                if type(image_field) is not ImageField:
                    image_field = None

            if image_field is None:
                if get_image_field_class_method is None:
                    errors.append(Critical(
                        msg=('Error in %(location)s: model %(model)s must '
                             'either have a field named "image" '
                             'or has a classmethod named "get_image_field", '
                             'which returns the image field of the model'
                             % {"location": "'%s' in '%s'" % (
                                    DEFAULT_TARGET_IMAGE_MODEL,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "model": default_target_image_model
                                }),
                        id="django-gallery-widget-default_image_model.E004"
                    ))
                else:
                    errors.append(Critical(
                        msg=('Error in %(location)s: model %(model)s defined '
                             '"get_image_field" class method '
                             'did not return a ImageField type'
                             % {"location": "'%s' in '%s'" % (
                                    DEFAULT_TARGET_IMAGE_MODEL,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "model": default_target_image_model
                                }),
                        id="django-gallery-widget-default_image_model.E005"
                    ))

    assets = conf.get(ASSETS, None)
    if assets is not None:
        if not isinstance(assets, dict):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": "'%s' in '%s'" % (
                            ASSETS, DJANGO_GALLERY_WIDGET_CONFIG),
                        "types": "dict"}),
                id="django-gallery-widget-assets.E001"
            ))
        else:
            bootstrap_js_path = assets.get(BOOTSTRAP_JS_PATH, None)
            if (bootstrap_js_path is not None
                    and not isinstance(bootstrap_js_path, str)):
                errors.append(DJGalleryCriticalCheckMessage(
                    msg=(INSTANCE_ERROR_PATTERN
                         % {"location": "'%s' in '%s' in '%s'" % (
                                BOOTSTRAP_JS_PATH, ASSETS,
                                DJANGO_GALLERY_WIDGET_CONFIG),
                            "types": "str"}),
                    id="django-gallery-widget-assets.E002"
                ))

            bootstrap_css_path = assets.get(BOOTSTRAP_CSS_PATH, None)
            if (bootstrap_css_path is not None
                    and not isinstance(bootstrap_css_path, str)):
                errors.append(DJGalleryCriticalCheckMessage(
                    msg=(INSTANCE_ERROR_PATTERN
                         % {"location": "'%s' in '%s' in '%s'" % (
                                BOOTSTRAP_CSS_PATH, ASSETS,
                                DJANGO_GALLERY_WIDGET_CONFIG),
                            "types": "str"}),
                    id="django-gallery-widget-assets.E003"
                ))

            jquery_js_path = assets.get(JQUERY_JS_PATH, None)
            if (jquery_js_path is not None
                    and not isinstance(jquery_js_path, str)):
                errors.append(DJGalleryCriticalCheckMessage(
                    msg=(INSTANCE_ERROR_PATTERN
                         % {"location": "'%s' in '%s' in '%s'" % (
                                JQUERY_JS_PATH, ASSETS,
                                DJANGO_GALLERY_WIDGET_CONFIG),
                            "types": "str"}),
                    id="django-gallery-widget-assets.E004"
                ))

            extra_js = assets.get(EXTRA_JS, None)
            if extra_js is not None:
                if not isinstance(extra_js, list):
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(INSTANCE_ERROR_PATTERN
                             % {"location": "'%s' in '%s' in '%s'" % (
                                    EXTRA_JS, ASSETS,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "types": "str"}),
                        id="django-gallery-widget-assets.E005"
                    ))
                else:
                    for js in extra_js:
                        if not isinstance(js, str):
                            errors.append(DJGalleryCriticalCheckMessage(
                                msg=(INSTANCE_ERROR_PATTERN % {
                                    "location":
                                        "'%s' in '%s' in '%s' in '%s'" % (
                                            str(js),
                                            EXTRA_JS, ASSETS,
                                            DJANGO_GALLERY_WIDGET_CONFIG),
                                    "types": "str"}),
                                id="django-gallery-widget-assets.E006"
                            ))

            extra_css = assets.get(EXTRA_CSS, None)
            if extra_css is not None:
                if not isinstance(extra_css, list):
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(INSTANCE_ERROR_PATTERN
                             % {"location": "'%s' in '%s' in '%s'" % (
                                    EXTRA_CSS, ASSETS,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "types": "str"}),
                        id="django-gallery-widget-assets.E007"
                    ))
                else:
                    for css in extra_css:
                        if not isinstance(css, str):
                            errors.append(DJGalleryCriticalCheckMessage(
                                msg=(INSTANCE_ERROR_PATTERN % {
                                    "location":
                                        "'%s' in '%s' in '%s' in '%s'" % (
                                            str(css),
                                            EXTRA_CSS, ASSETS,
                                            DJANGO_GALLERY_WIDGET_CONFIG),
                                    "types": "str"}),
                                id="django-gallery-widget-assets.E008"
                            ))

    thumbnails = conf.get(THUMBNAILS, None)
    if thumbnails is not None:
        if not isinstance(thumbnails, dict):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": "'%s' in '%s'" % (
                            THUMBNAILS, DJANGO_GALLERY_WIDGET_CONFIG),
                        "types": "dict"}),
                id="django-gallery-widget-thumbnails.E001"
            ))
        else:
            thumbnail_size = thumbnails.get(THUMBNAIL_SIZE, None)
            if thumbnail_size is not None:
                try:
                    _size = float(thumbnail_size)
                except Exception as e:
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(GENERIC_ERROR_PATTERN
                             % {"location": "'%s' in '%s' in '%s'" % (
                                    THUMBNAIL_SIZE, THUMBNAILS,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "error_type": type(e).__name__,
                                "error_str": str(e)}
                             ),
                        id="django-gallery-widget-thumbnails.E002"
                    ))
                else:
                    if _size < 0:
                        errors.append(DJGalleryCriticalCheckMessage(
                            msg=(GENERIC_ERROR_PATTERN
                                 % {"location": "'%s' in '%s' in '%s'" % (
                                        THUMBNAIL_QUALITY, THUMBNAILS,
                                        DJANGO_GALLERY_WIDGET_CONFIG),
                                    "error_type": TypeError.__name__,
                                    "error_str":
                                        "Thumbnail size should be a positive number"}
                                 ),
                            id="django-gallery-widget-thumbnails.E003"
                        ))

            thumbnail_quality = thumbnails.get(THUMBNAIL_QUALITY, None)
            if thumbnail_quality is not None:
                try:
                    quality = float(thumbnail_quality)
                except Exception as e:
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(GENERIC_ERROR_PATTERN
                             % {"location": "'%s' in '%s' in '%s'" % (
                                    THUMBNAIL_QUALITY, THUMBNAILS,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "error_type": type(e).__name__,
                                "error_str": str(e)}
                             ),
                        id="django-gallery-widget-thumbnails.E004"
                    ))
                else:
                    if quality < 0 or quality > 100:
                        errors.append(DJGalleryCriticalCheckMessage(
                            msg=(GENERIC_ERROR_PATTERN
                                 % {"location": "'%s' in '%s' in '%s'" % (
                                        THUMBNAIL_QUALITY, THUMBNAILS,
                                        DJANGO_GALLERY_WIDGET_CONFIG),
                                    "error_type": TypeError.__name__,
                                    "error_str":
                                        "Thumbnail quality should be "
                                        "between 0 and 100"}
                                 ),
                            id="django-gallery-widget-thumbnails.E005"
                        ))

    widget_hidden_input_css_class = conf.get(
        WIDGET_HIDDEN_INPUT_CSS_CLASS, None)

    if widget_hidden_input_css_class is not None:
        if not isinstance(widget_hidden_input_css_class, str):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": "'%s' in '%s'" % (
                            WIDGET_HIDDEN_INPUT_CSS_CLASS,
                            DJANGO_GALLERY_WIDGET_CONFIG),
                        "types": "str"}),
                id="django-gallery-widget-widget_hidden_input_css_class.E001"
            ))

    prompt_alert_if_changed_on_window_reload = conf.get(
        PROMPT_ALERT_IF_CHANGED_ON_WINDOW_RELOAD, None)

    if prompt_alert_if_changed_on_window_reload is not None:
        if not isinstance(prompt_alert_if_changed_on_window_reload, bool):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": "'%s' in '%s'" % (
                            PROMPT_ALERT_IF_CHANGED_ON_WINDOW_RELOAD,
                            DJANGO_GALLERY_WIDGET_CONFIG),
                        "types": "bool"}),
                id="django-gallery-widget-prompt_alert_if_changed_on_window_reload.E001"  # noqa
            ))

    return errors
