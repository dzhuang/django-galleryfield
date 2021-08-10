from django.conf import settings
from django.core import checks

from gallery.utils import (
    DJGalleryCriticalCheckMessage, INSTANCE_ERROR_PATTERN,
    GENERIC_ERROR_PATTERN, apps
)

from gallery import defaults


DJANGO_GALLERY_WIDGET_CONFIG = "DJANGO_GALLERY_WIDGET_CONFIG"

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
            assets_copy = assets.copy()
            extra_js = assets_copy.pop(EXTRA_JS, None)
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

            extra_css = assets_copy.pop(EXTRA_CSS, None)
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

            for asset_name, asset_value in assets_copy.items():
                if asset_name not in (
                        defaults.VENDER_CSS_NAMES + defaults.VENDER_JS_NAMES):
                    errors.append(checks.Warning(
                        msg=("%(location)s is not in the required assets, it"
                             "you want to use it, put it in %(extra_css)s or "
                             "%(extra_js)s"
                             % {"location": (
                                        "Asset '%s' in '%s' in '%s'" % (
                                            str(asset_name), ASSETS,
                                            DJANGO_GALLERY_WIDGET_CONFIG)),
                                 "extra_js": EXTRA_JS,
                                 "extra_css": EXTRA_CSS}
                             ),
                        id="django-gallery-widget-assets.W001"
                    ))
                    continue

                if asset_value is None:
                    errors.append(checks.Warning(
                        msg=("%(location)s is set to None, that might "
                             "cause unexpected result in views as well "
                             "as in admin."
                             % {"location": (
                                        "Asset '%s' in '%s' in '%s'" % (
                                            str(asset_name), ASSETS,
                                            DJANGO_GALLERY_WIDGET_CONFIG))}
                             ),
                        id="django-gallery-widget-assets.W002"
                    ))
                    continue

                # Note the asset_value is not necessary a str, it can be a
                # JS object (see django-js-asset).

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
