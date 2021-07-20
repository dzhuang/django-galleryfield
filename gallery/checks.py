from django.conf import settings
from django.core.checks import Critical, Warning, register
from django.core.exceptions import ImproperlyConfigured, FieldDoesNotExist
from django.utils.module_loading import import_string
from django.apps import apps
from django.urls import reverse


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

ASSETS = "assets"
BOOTSTRAP_JS_PATH = "bootstrap_js_path"
BOOTSTRAP_CSS_PATH = "bootstrap_css_path"
JQUERY_JS_PATH = "jquery_js_path"
EXTRA_JS = "extra_js"
EXTRA_CSS = "extra_css"

THUMBNAILS = "thumbnails"
THUMBNAIL_SIZE = "size"
THUMBNAIL_QUALITY = "quality"

MULTIFIELD_CSS_CLASS_BASENAME = "multifield_css_class_basename"

PROMPT_ALERT_IF_CHANGED_ON_WINDOW_RELOAD = (
    "prompt_alert_if_changed_on_window_reload")

DEFAULT_IMAGE_INSTANCE_HANDLE_BACKEND = "default_image_instance_handle_backend"


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
                id="django-gallery-widget-default-urls.E001"
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
                        id="django-gallery-widget-default-urls.E002"
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
                            id="django-gallery-widget-default-urls.E003"
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
                        id="django-gallery-widget-default-urls.E004"
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
                            id="django-gallery-widget-default-urls.E005"
                        ))

        default_image_model = conf.get(DEFAULT_IMAGE_MODEL, None)
        if default_image_model is not None:
            if not isinstance(default_urls, dict):
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

                will_check_image_field = True
                if target_image_model is not None and target_model is None:
                    # errored in checking target_image_model
                    will_check_image_field = False

                target_image_field_name = default_image_model.get(
                    TARGET_IMAGE_FIELD_NAME, None)
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

                if will_check_image_field:
                    if target_image_field_name is None:
                        target_image_field_name = (
                            app_conf.DEFAULT_TARGET_IMAGE_FIELD_NAME)
                    if target_model is None:
                        target_model = apps.get_model(
                            app_conf.DEFAULT_TARGET_IMAGE_MODEL)

                    try:
                        target_model._meta.get_field(target_image_field_name)
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
                        for css in extra_js:
                            if not isinstance(css, str):
                                errors.append(DJGalleryCriticalCheckMessage(
                                    msg=(INSTANCE_ERROR_PATTERN % {
                                        "location":
                                            "'%s' in '%s' in '%s' in '%s'" % (
                                                css,
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
                                                css,
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
                try:
                    int(thumbnail_size)
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

                thumbnail_quality = thumbnails.get(THUMBNAIL_QUALITY, None)
                try:
                    int(thumbnail_quality)
                except Exception as e:
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(GENERIC_ERROR_PATTERN
                             % {"location": "'%s' in '%s' in '%s'" % (
                                    THUMBNAIL_QUALITY, THUMBNAILS,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "error_type": type(e).__name__,
                                "error_str": str(e)}
                             ),
                        id="django-gallery-widget-thumbnails.E003"
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

        default_image_instance_handle_backend = conf.get(
            DEFAULT_IMAGE_INSTANCE_HANDLE_BACKEND, None
        )

        if default_image_instance_handle_backend is not None:
            if not isinstance(default_image_instance_handle_backend, str):
                errors.append(DJGalleryCriticalCheckMessage(
                    msg=(INSTANCE_ERROR_PATTERN
                         % {"location": "'%s' in '%s'" % (
                                DEFAULT_IMAGE_INSTANCE_HANDLE_BACKEND,
                                DJANGO_GALLERY_WIDGET_CONFIG),
                            "types": "bool"}),
                    id="django-gallery-widget-default_image_instance_handle_backend.E001"  # noqa
                ))
            else:
                try:
                    import_string(default_image_instance_handle_backend)
                except Exception as e:
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(GENERIC_ERROR_PATTERN
                             % {"location": "'%s' in '%s'" % (
                                    DEFAULT_IMAGE_INSTANCE_HANDLE_BACKEND,
                                    DJANGO_GALLERY_WIDGET_CONFIG),
                                "error_type": type(e).__name__,
                                "error_str": str(e)}
                             ),
                        id="django-gallery-widget-default_image_instance_handle_backend.E002"  # noqa
                    ))

    return errors
