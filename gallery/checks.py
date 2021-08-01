from django.conf import settings
from django.core import checks
from django.urls import reverse

from gallery.utils import (
    DJGalleryCriticalCheckMessage, INSTANCE_ERROR_PATTERN,
    GENERIC_ERROR_PATTERN,
    get_or_check_image_field, apps
)


DJANGO_GALLERY_WIDGET_CONFIG = "DJANGO_GALLERY_WIDGET_CONFIG"
DEFAULT_URLS = "default_urls"
UPLOAD_HANDLER_URL_NAME = "upload_handler_url_name"
FETCH_URL_NAME = "fetch_url_name"
CROP_URL_NAME = "crop_url_name"

DEFAULT_TARGET_IMAGE_MODEL = "default_target_image_model"

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
    checks.register(check_settings, "django_gallery_widget_checks")


def check_settings(app_configs, **kwargs):
    errors = []

    if not apps.is_installed('sorl.thumbnail'):
        missing_app = checks.Error(
            "'sorl.thumbnail' must be in INSTALLED_APPS in order "
            "to generate thumbnail for gallery images.",
            id="django-gallery-widget.E001",
        )
        errors.append(missing_app)

    conf = getattr(settings, "DJANGO_GALLERY_WIDGET_CONFIG", None)
    if conf is None:
        return errors

    if not isinstance(conf, dict):
        errors.append(DJGalleryCriticalCheckMessage(
            msg=(INSTANCE_ERROR_PATTERN
                 % {"location": DJANGO_GALLERY_WIDGET_CONFIG, "types": "dict"}),
            id="django-gallery-widget.E002"
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

    default_target_image_model = conf.get(DEFAULT_TARGET_IMAGE_MODEL, None)
    location = "'%s' in '%s'" % (
        DEFAULT_TARGET_IMAGE_MODEL, DJANGO_GALLERY_WIDGET_CONFIG)

    errors.extend(get_or_check_image_field(
        target_app_model_str=default_target_image_model,
        location=location,
        check_id_prefix="django-gallery-widget-default_target_image_model",
        is_checking=True
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
