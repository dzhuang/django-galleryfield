from django.conf import settings
from django.core.checks import Critical, Warning, register
from django.core.exceptions import ImproperlyConfigured, FieldDoesNotExist

try:  # pragma: no cover
    from django.apps import apps
except ImportError:  # pragma: no cover
    from django.apps import django_apps as apps

from django.urls import reverse
from django.db.models import ImageField, ForeignKey

from . import conf as app_conf

REQUIRED_CONF_ERROR_PATTERN = (
    "You must configure %(location)s for RELATE to run properly.")
INSTANCE_ERROR_PATTERN = "%(location)s must be an instance of %(types)s."
GENERIC_ERROR_PATTERN = "Error in %(location)s: %(error_type)s: %(error_str)s"

DJANGO_GALLERY_WIDGET_CONFIG = "DJANGO_GALLERY_WIDGET_CONFIG"
DEFAULT_URLS = "default_urls"
UPLOAD_HANDLER_URL_NAME = "upload_handler_url_name"
CROP_URL_NAME = "crop_url_name"
DEFAULT_IMAGE_MODEL = "default_image_model"
TARGET_IMAGE_MODEL = "target_image_model"
TARGET_IMAGE_FIELD_NAME = "target_image_field_name"
TARGET_CREATOR_FIELD_NAME = "target_creator_field_name"

ASSETS = "assets"
BOOTSTRAP_JS_PATH = "bootstrap_js_path"
BOOTSTRAP_CSS_PATH = "bootstrap_css_path"
JQUERY_JS_PATH = "jquery_js_path"
EXTRA_JS = "extra_js"
EXTRA_CSS = "extra_css"

THUMBNAILS = "thumbnails"
THUMBNAIL_SIZE = "size"
THUMBNAIL_QUALITY = "quality"

FIELD_HACK = "field_hack"
OLD_VALUE_STR = "old_value_str"
DELETED_VALUE_STR = "deleted_value_str"

MULTIFIELD_CSS_CLASS_BASENAME = "multifield_css_class_basename"

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

    default_image_model = conf.get(DEFAULT_IMAGE_MODEL, None)
    will_check_model_fields = True
    if default_image_model is not None:
        if not isinstance(default_image_model, dict):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": "'%s' in '%s'" % (
                            DEFAULT_IMAGE_MODEL, DJANGO_GALLERY_WIDGET_CONFIG),
                        "types": "dict"}),
                id="django-gallery-widget-default_image_model.E001"
            ))
        else:
            target_image_model = default_image_model.get(
                TARGET_IMAGE_MODEL, None)
            target_model = None
            if target_image_model is not None:
                if not isinstance(target_image_model, str):
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(INSTANCE_ERROR_PATTERN
                             % {"location": "'%s' in '%s' in '%s'" % (
                                    TARGET_IMAGE_MODEL, DEFAULT_IMAGE_MODEL,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "types": "str"}),
                        id="django-gallery-widget-default_image_model.E002"
                    ))
                    will_check_model_fields = False
                else:
                    try:
                        target_model = apps.get_model(target_image_model)
                    except Exception as e:
                        errors.append(DJGalleryCriticalCheckMessage(
                            msg=(GENERIC_ERROR_PATTERN
                                 % {"location": "'%s' in '%s' in '%s'" % (
                                        TARGET_IMAGE_MODEL, DEFAULT_IMAGE_MODEL,
                                        DJANGO_GALLERY_WIDGET_CONFIG),
                                    "error_type": type(e).__name__,
                                    "error_str": str(e)}
                                 + "\n See "
                                   "https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.get_model"  # noqa
                                   " for more information."
                                 ),
                            id="django-gallery-widget-default_image_model.E003"
                        ))
                        will_check_model_fields = False

            if will_check_model_fields:
                target_image_field_name = default_image_model.get(
                    TARGET_IMAGE_FIELD_NAME, None)
                will_proceed_image_field_validation = True
                if target_image_field_name is not None:
                    if not isinstance(target_image_field_name, str):
                        errors.append(DJGalleryCriticalCheckMessage(
                            msg=(INSTANCE_ERROR_PATTERN
                                 % {"location": "'%s' in '%s' in '%s'" % (
                                        TARGET_IMAGE_FIELD_NAME,
                                        DEFAULT_IMAGE_MODEL,
                                        DJANGO_GALLERY_WIDGET_CONFIG),
                                    "types": "str"}),
                            id="django-gallery-widget-default_image_model.E004"
                        ))
                        will_proceed_image_field_validation = False

                else:
                    target_image_field_name = (
                        app_conf.DEFAULT_TARGET_IMAGE_FIELD_NAME)

                assert target_image_field_name is not None

                if will_proceed_image_field_validation:
                    if target_model is None:
                        target_model = apps.get_model(
                            app_conf.DEFAULT_TARGET_IMAGE_MODEL)

                    try:
                        image_field = target_model._meta.get_field(target_image_field_name)
                    except FieldDoesNotExist as e:
                        errors.append(DJGalleryCriticalCheckMessage(
                            msg=(GENERIC_ERROR_PATTERN
                                 % {"location": "'%s' in '%s' in '%s'" % (
                                        TARGET_IMAGE_MODEL, DEFAULT_IMAGE_MODEL,
                                        DJANGO_GALLERY_WIDGET_CONFIG),
                                    "error_type": type(e).__name__,
                                    "error_str": str(e)}
                                 ),
                            id="django-gallery-widget-default_image_model.E005"
                        ))
                    else:
                        if type(image_field) is not ImageField:
                            errors.append(DJGalleryCriticalCheckMessage(
                                msg=(GENERIC_ERROR_PATTERN
                                     % {"location": "'%s' in '%s' in '%s'" % (
                                            TARGET_IMAGE_MODEL, DEFAULT_IMAGE_MODEL,
                                            DJANGO_GALLERY_WIDGET_CONFIG),
                                        "error_type": type(TypeError).__name__,
                                        "error_str":
                                            "%s is not an ImageField"
                                            % target_image_field_name}
                                     ),
                                id="django-gallery-widget-default_image_model.E006"
                            ))

                target_creator_field_name = default_image_model.get(
                    TARGET_CREATOR_FIELD_NAME, None)
                will_proceed_creator_field_validation = True
                if target_creator_field_name is not None:
                    if not isinstance(target_creator_field_name, str):
                        errors.append(DJGalleryCriticalCheckMessage(
                            msg=(INSTANCE_ERROR_PATTERN
                                 % {"location": "'%s' in '%s' in '%s'" % (
                                        TARGET_CREATOR_FIELD_NAME,
                                        DEFAULT_IMAGE_MODEL,
                                        DJANGO_GALLERY_WIDGET_CONFIG),
                                    "types": "str"}),
                            id="django-gallery-widget-default_image_model.E007"
                        ))
                        will_proceed_creator_field_validation = False

                else:
                    target_creator_field_name = (
                        app_conf.DEFAULT_CREATOR_FIELD_NAME)

                assert target_creator_field_name is not None

                if will_proceed_creator_field_validation:
                    if target_model is None:
                        target_model = apps.get_model(
                            app_conf.DEFAULT_TARGET_IMAGE_MODEL)

                    try:
                        creator_field = target_model._meta.get_field(target_creator_field_name)
                    except FieldDoesNotExist as e:
                        errors.append(DJGalleryCriticalCheckMessage(
                            msg=(GENERIC_ERROR_PATTERN
                                 % {"location": "'%s' in '%s' in '%s'" % (
                                        TARGET_CREATOR_FIELD_NAME, DEFAULT_IMAGE_MODEL,
                                        DJANGO_GALLERY_WIDGET_CONFIG),
                                    "error_type": type(e).__name__,
                                    "error_str": str(e)}
                                 ),
                            id="django-gallery-widget-default_image_model.E008"
                        ))
                    else:
                        if type(creator_field) is not ForeignKey:
                            errors.append(DJGalleryCriticalCheckMessage(
                                msg=(GENERIC_ERROR_PATTERN
                                     % {"location": "'%s' in '%s' in '%s'" % (
                                            TARGET_IMAGE_MODEL, DEFAULT_IMAGE_MODEL,
                                            DJANGO_GALLERY_WIDGET_CONFIG),
                                        "error_type": type(TypeError).__name__,
                                        "error_str":
                                            "%s is not a ForeignKey user model of"
                                            " target image model."
                                            % target_image_field_name}
                                     ),
                                id="django-gallery-widget-default_image_model.E009"
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
                                        "Thumbnail quality should be between 0 and 100"}
                                 ),
                            id="django-gallery-widget-thumbnails.E005"
                        ))

    field_hack = conf.get(FIELD_HACK, None)
    field_hack_has_error = False
    if field_hack is not None:
        if not isinstance(field_hack, dict):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(FIELD_HACK
                     % {"location": "'%s' in '%s'" % (
                            FIELD_HACK, DJANGO_GALLERY_WIDGET_CONFIG),
                        "types": "dict"}),
                id="django-gallery-widget-field_hack.E001"
            ))
            field_hack_has_error = True
        else:
            old_value_str = field_hack.get(OLD_VALUE_STR, None)
            if old_value_str is not None:
                if not isinstance(old_value_str, str):
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(INSTANCE_ERROR_PATTERN
                             % {"location": "'%s' in '%s' in '%s'" % (
                                    OLD_VALUE_STR, FIELD_HACK,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "types": "str"}),
                        id="django-gallery-widget-field_hack.E002"
                    ))
                    field_hack_has_error = True
                else:
                    try:
                        old_value_str % "image_field_name"
                    except Exception as e:
                        errors.append(DJGalleryCriticalCheckMessage(
                            msg=(GENERIC_ERROR_PATTERN
                                 % {"location": "'%s' in '%s' in '%s'" % (
                                        OLD_VALUE_STR, FIELD_HACK,
                                        DJANGO_GALLERY_WIDGET_CONFIG),
                                    "error_type": type(e).__name__,
                                    "error_str": str(e)}
                                 ),
                            id="django-gallery-widget-field_hack.E003"
                        ))
                        field_hack_has_error = True

            deleted_value_str = field_hack.get(DELETED_VALUE_STR, None)
            if deleted_value_str is not None:
                if not isinstance(deleted_value_str, str):
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(INSTANCE_ERROR_PATTERN
                             % {"location": "'%s' in '%s' in '%s'" % (
                                    DELETED_VALUE_STR, FIELD_HACK,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "types": "str"}),
                        id="django-gallery-widget-field_hack.E004"
                    ))
                    field_hack_has_error = True
                else:
                    try:
                        deleted_value_str % "image_field_name"
                    except Exception as e:
                        errors.append(DJGalleryCriticalCheckMessage(
                            msg=(GENERIC_ERROR_PATTERN
                                 % {"location": "'%s' in '%s' in '%s'" % (
                                        DELETED_VALUE_STR, FIELD_HACK,
                                        DJANGO_GALLERY_WIDGET_CONFIG),
                                    "error_type": type(e).__name__,
                                    "error_str": str(e)}
                                 ),
                            id="django-gallery-widget-field_hack.E005"
                        ))
                        field_hack_has_error = True

            if not field_hack_has_error:
                old_value_str = old_value_str or app_conf.OLD_VALUE_STR
                deleted_value_str = deleted_value_str or app_conf.DELETED_VALUE_STR
                if old_value_str == deleted_value_str:
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(GENERIC_ERROR_PATTERN
                             % {"location": "'%s' and '%s' in '%s' in '%s'" % (
                                    OLD_VALUE_STR, DELETED_VALUE_STR, FIELD_HACK,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "error_type": "",
                                "error_str": "'%s' and '%s' should not be the same" % (
                                    OLD_VALUE_STR, DELETED_VALUE_STR
                                )}
                             ),
                        id="django-gallery-widget-field_hack.E006"
                    ))

    multifield_css_class_basename = conf.get(
        MULTIFIELD_CSS_CLASS_BASENAME, None)

    if multifield_css_class_basename is not None:
        if not isinstance(multifield_css_class_basename, str):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": "'%s' in '%s'" % (
                            MULTIFIELD_CSS_CLASS_BASENAME,
                            DJANGO_GALLERY_WIDGET_CONFIG),
                        "types": "str"}),
                id="django-gallery-widget-multifield_css_class_basename.E001"
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
