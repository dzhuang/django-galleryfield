from django.conf import settings
from . import defaults

"""
DJANGO_GALLERY_WIDGET_CONFIG = {
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


PROMPT_ALERT_ON_WINDOW_RELOAD_IF_CHANGED = _APP_CONFIG.get(
    'prompt_alert_if_changed_on_window_reload',
    defaults.PROMPT_ALERT_ON_WINDOW_RELOAD_IF_CHANGED
)

# BE CAUTIOUS: changing the sequence of the assets
# might result in failure to render the widget
_js_items = (
    'jquery.js',
    'jquery-ui.js',
    'jquery.ui.widget.min.js',
    'blueimp-tmpl.js',
    'load-image.all.min.js',
    'blueimp-canvas-to-blob.js',
    'bootstrap.js',
    'jquery.iframe-transport.js',
    'jquery.fileupload.js',
    'jquery.fileupload-process.js',
    'jquery.fileupload-image.js',
    'jquery.fileupload-audio.js',
    'jquery.fileupload-video.js',
    'jquery.fileupload-validate.js',
    'jquery.fileupload-ui.js',
    'jquery.blueimp-gallery.js',
    'blueimp-gallery-indicator.js',
    'blueimp-gallery-fullscreen.js',
    'cropper.js')

_css_items = (
    'bootstrap.css',
    'jquery-ui.theme.css',
    'jquery.fileupload.css',
    'jquery.fileupload-ui.css',
    'blueimp-gallery.css',
    'blueimp-gallery-indicator.css',
    'font-awesome.css',
    'cropper.css')

_new_assets = defaults.DEFAULT_ASSETS.copy()
_app_config_assets_copy = _APP_CONFIG_ASSETS.copy()
_extra_js = _app_config_assets_copy.pop("extra_js", [])
_extra_js.append("js/jquery.fileupload-ui-gallery-widget.js")
_extra_css = _app_config_assets_copy.pop("extra_css", [])

_new_assets.update(_app_config_assets_copy)

_js = [_new_assets.get(v) for v in _js_items] + _extra_js
JS = [j for j in _js if j]

_css = [_new_assets.get(v) for v in _css_items] + _extra_css
CSS = [c for c in _css if c]
