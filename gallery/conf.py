from django.conf import settings
from . import defaults

"""
DJANGO_GALLERY_WIDGET_CONFIG = {
    "default_urls":
        {"upload_handler_url_name": "gallery_image_upload",
         "fetch_url_name": "gallery_images_fetch",
         "crop_url_name": "gallery_image_crop"},
    "default_target_image_model": "gallery.BuiltInGalleryImage",
    "assets": {
        "bootstrap_js_path": 'vendor/bootstrap/dist/js/bootstrap.min.js',
        "bootstrap_css_path": "vendor/bootstrap/dist/css/bootstrap.min.css",
        "jquery_js_path": "vendor/jquery.min.js",
        "extra_js": [],
        "extra_css": [],
    },
    "thumbnails": {
        "size": 120,
        "quality": 80
    },
    "widget_hidden_input_css_class": "django-gallery-widget",
    "prompt_alert_if_changed_on_window_reload": True,
}
"""


_APP_CONFIG = getattr(settings, "DJANGO_GALLERY_WIDGET_CONFIG", {})

_APP_CONFIG_URLS = _APP_CONFIG.get("default_urls", {})
DEFAULT_UPLOAD_HANDLER_URL_NAME = _APP_CONFIG_URLS.get(
    "upload_handler_url_name", defaults.DEFAULT_UPLOAD_HANDLER_URL_NAME)
DEFAULT_CROP_URL_NAME = _APP_CONFIG_URLS.get(
    "crop_url_name", defaults.DEFAULT_CROP_URL_NAME)
DEFAULT_FETCH_URL_NAME = _APP_CONFIG_URLS.get(
    "fetch_image_url_name", defaults.DEFAULT_FETCH_URL_NAME
)

DEFAULT_TARGET_IMAGE_MODEL = _APP_CONFIG.get(
    "default_target_image_model", defaults.DEFAULT_TARGET_IMAGE_MODEL)

_APP_CONFIG_ASSETS = _APP_CONFIG.get("assets", {})
BOOTSTRAP_JS_PATH = _APP_CONFIG_ASSETS.get(
    "bootstrap_js_path", defaults.BOOTSTRAP_JS_PATH)
BOOTSTRAP_CSS_PATH = _APP_CONFIG_ASSETS.get(
    "bootstrap_css_path", defaults.BOOTSTRAP_CSS_PATH)
JQUERY_JS_PATH = _APP_CONFIG_ASSETS.get(
    "jquery_js_path", defaults.JQUERY_JS_PATH)
EXTRA_JS = _APP_CONFIG_ASSETS.get("extra_js", defaults.EXTRA_JS)
EXTRA_CSS = _APP_CONFIG_ASSETS.get("extra_css", defaults.EXTRA_CSS)


_APP_CONFIG_THUMBNAILS = _APP_CONFIG.get("thumbnails", {})
DEFAULT_THUMBNAIL_SIZE = int(_APP_CONFIG_THUMBNAILS.get(
    "size", defaults.DEFAULT_THUMBNAIL_SIZE))
DEFAULT_THUMBNAIL_QUALITY = int(_APP_CONFIG_THUMBNAILS.get(
    "quality", defaults.DEFAULT_THUMBNAIL_QUALITY))


_APP_CONFIG_FIELD_VALUE_NAME_HACK = _APP_CONFIG.get("field_hack", {})
OLD_VALUE_STR = _APP_CONFIG_FIELD_VALUE_NAME_HACK.get(
    'old_value_str', defaults.OLD_VALUE_STR)
DELETED_VALUE_STR = _APP_CONFIG_FIELD_VALUE_NAME_HACK.get(
    'deleted_value_str', defaults.DELETED_VALUE_STR)


_APP_CONFIG_WIDGET_INPUT_CSS_CLASS = _APP_CONFIG.get(
    "widget_hidden_input_css_class", defaults.WIDGET_HIDDEN_INPUT_CSS_CLASS)
FILES_FIELD_CLASS_NAME = _APP_CONFIG_WIDGET_INPUT_CSS_CLASS + "-files-field"
DELETED_FIELD_CLASS_NAME = _APP_CONFIG_WIDGET_INPUT_CSS_CLASS + "-deleted-field"


PROMPT_ALERT_ON_WINDOW_RELOAD_IF_CHANGED = _APP_CONFIG.get(
    'prompt_alert_if_changed_on_window_reload',
    defaults.PROMPT_ALERT_ON_WINDOW_RELOAD_IF_CHANGED
)
