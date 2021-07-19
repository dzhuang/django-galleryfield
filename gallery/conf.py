from django.conf import settings

"""
DJANGO_GALLERY_CONFIG = {
    "default_urls": 
        {"upload_handler_url_name": "gallery_image_upload",
         "crop_url_name": "crop"},
    "default_image_model":
        {"target_image_model": "gallery.BuiltInGalleryImage",
         "target_image_field_name": "image"},
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
    "field_hack": {
        "old_value_str": 'old_%s_value',
        "deleted_value_str": 'deleted_%s_value',
        "moved_value_str": "moved_%s_value"
    },
    "multifield_css_class_basename": "django-gallery-widget",
    "prompt_alert_if_changed_on_window_reload": True,
    "default_image_instance_handle_backend": 
        'gallery.backends.backend.BackendWithThumbnailField'
}
"""


_APP_CONFIG = getattr(settings, "DJANGO_GALLERY_CONFIG", {})

_APP_CONFIG_URLS = _APP_CONFIG.get("default_urls", {})
DEFAULT_UPLOAD_HANDLER_URL_NAME = _APP_CONFIG_URLS.get(
    "upload_handler_url_name", "gallery_image_upload")
DEFAULT_CROP_URL_NAME = _APP_CONFIG_URLS.get(
    "crop_url_name", "gallery_image_crop")


_APP_CONFIG_IMAGE_MODEL = _APP_CONFIG.get("default_image_model", {})
DEFAULT_TARGET_IMAGE_MODEL = _APP_CONFIG_IMAGE_MODEL.get(
    "default_target_image_model", "gallery.BuiltInGalleryImage")
DEFAULT_TARGET_IMAGE_FIELD_NAME = _APP_CONFIG_IMAGE_MODEL.get(
    "default_target_image_field_name", "image")


_APP_CONFIG_ASSETS = _APP_CONFIG.get("assets", {})
BOOTSTRAP_JS_PATH = _APP_CONFIG_ASSETS.get(
    "bootstrap_js_path", 'vendor/bootstrap/dist/js/bootstrap.min.js')
BOOTSTRAP_CSS_PATH = _APP_CONFIG_ASSETS.get(
    "bootstrap_css_path", 'vendor/bootstrap/dist/css/bootstrap.min.css')
JQUERY_JS_PATH = _APP_CONFIG_ASSETS.get(
    "jquery_js_path", "vendor/jquery.min.js")
EXTRA_JS = _APP_CONFIG_ASSETS.get("extra_js", [])
EXTRA_CSS = _APP_CONFIG_ASSETS.get("extra_css", [])


_APP_CONFIG_THUMBNAILS = _APP_CONFIG.get("thumbnails", {})
DEFAULT_THUMBNAIL_SIZE = int(_APP_CONFIG_THUMBNAILS.get(
    "size", 120))
DEFAULT_THUMBNAIL_QUALITY = int(_APP_CONFIG_THUMBNAILS.get(
    "quality", 80))


_APP_CONFIG_FIELD_VALUE_NAME_HACK = _APP_CONFIG.get("field_hack", {})
OLD_VALUE_STR = _APP_CONFIG_FIELD_VALUE_NAME_HACK.get(
    'old_value_str', 'old_%s_value')
DELETED_VALUE_STR = _APP_CONFIG_FIELD_VALUE_NAME_HACK.get(
    'deleted_value_str', 'deleted_%s_value')
MOVED_VALUE_STR = _APP_CONFIG_FIELD_VALUE_NAME_HACK.get(
    'moved_value_str', 'moved_%s_value')


_APP_CONFIG_WIDGET_INPUT_CSS_CLASS = _APP_CONFIG.get(
    "multifield_css_class_basename", "django-gallery-widget")
FILES_FIELD_CLASS_NAME = _APP_CONFIG_WIDGET_INPUT_CSS_CLASS + "-files-field"
DELETED_FIELD_CLASS_NAME = _APP_CONFIG_WIDGET_INPUT_CSS_CLASS + "-deleted-field"
MOVED_FIELD_CLASS_NAME = _APP_CONFIG_WIDGET_INPUT_CSS_CLASS + "-moved-field"


PROMPT_ALERT_ON_WINDOW_RELOAD_IF_CHANGED = _APP_CONFIG.get(
    'prompt_alert_if_changed_on_window_reload', True)


DEFAULT_BACKEND = _APP_CONFIG.get(
    "default_image_instance_handle_backend",
    'gallery.backends.backend.BackendWithThumbnailField')
