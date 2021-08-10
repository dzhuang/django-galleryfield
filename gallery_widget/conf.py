from django.conf import settings
from . import defaults
from .utils import get_formatted_thumbnail_size

"""
DJANGO_GALLERY_WIDGET_CONFIG = {
    "assets": {
        "jquery.js": 'http://example.com/jquery.js',
        "bootstrap.css": "/my/local/bootstrap.css",
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

# {{{ Generating js and css assets for GalleryWidget

_APP_CONFIG_ASSETS = _APP_CONFIG.get("assets", {})
EXTRA_JS = _APP_CONFIG_ASSETS.pop("extra_js", defaults.EXTRA_JS)
EXTRA_CSS = _APP_CONFIG_ASSETS.pop("extra_css", defaults.EXTRA_CSS)

_assets = defaults.DEFAULT_ASSETS.copy()
_assets.update(_APP_CONFIG_ASSETS)

_js = [_assets.get(v) for v in defaults.VENDER_JS_NAMES]
_js.extend(defaults.BUILT_IN_JS + EXTRA_JS)
JS = [j for j in _js if j]

_css = [_assets.get(v) for v in defaults.VENDER_CSS_NAMES] + EXTRA_CSS
_css.extend(defaults.BUILT_IN_CSS + EXTRA_CSS)
CSS = [c for c in _css if c]

# }}}

# todo: allow 60x90 to thumbnail size and check
_APP_CONFIG_THUMBNAILS = _APP_CONFIG.get("thumbnails", {})
DEFAULT_THUMBNAIL_SIZE = get_formatted_thumbnail_size(
    _APP_CONFIG_THUMBNAILS.get(
        "size", defaults.DEFAULT_THUMBNAIL_SIZE))
DEFAULT_THUMBNAIL_QUALITY = int(_APP_CONFIG_THUMBNAILS.get(
    "quality", defaults.DEFAULT_THUMBNAIL_QUALITY))


_APP_CONFIG_WIDGET_INPUT_CSS_CLASS = _APP_CONFIG.get(
    "widget_hidden_input_css_class", defaults.WIDGET_HIDDEN_INPUT_CSS_CLASS)
FILES_FIELD_CLASS_NAME = _APP_CONFIG_WIDGET_INPUT_CSS_CLASS + "-files-field"


PROMPT_ALERT_ON_WINDOW_RELOAD_IF_CHANGED = _APP_CONFIG.get(
    'prompt_alert_if_changed_on_window_reload',
    defaults.PROMPT_ALERT_ON_WINDOW_RELOAD_IF_CHANGED
)

# todo: allow setting default jquery_fileupload_ui_options in settings.
