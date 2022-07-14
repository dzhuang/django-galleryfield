from django.conf import settings

from galleryfield import defaults
from galleryfield.utils import get_formatted_thumbnail_size

"""
DJANGO_GALLERY_FIELD_CONFIG = {
    "bootstrap_version": 3,
    "assets": {
        "jquery": '/path/to/my/local/jquery.js/or/cdn',
        "bootstrap_css": "/path/to/my/local/bootstrap.css/or/cdn",
        "bootstrap_js": "/path/to/my/local/bootstrap.js/or/cdn",
        "extra_js": [],
        "extra_css": [],
    },
    "thumbnails": {
        "size": 120,
        "quality": 80
    },
    "jquery_file_upload_ui_options": {}
    "jquery_file_upload_ui_sortable_options": {}
    "widget_hidden_input_css_class": "django-galleryfield",
    "prompt_alert_if_changed_on_window_reload": True,
}
"""


_APP_CONFIG = getattr(settings, "DJANGO_GALLERY_FIELD_CONFIG", {})

# {{{ Generating js and css assets for GalleryWidget

_APP_CONFIG_ASSETS = _APP_CONFIG.get("assets", {})
EXTRA_JS = _APP_CONFIG_ASSETS.pop("extra_js", None) or defaults.EXTRA_JS
EXTRA_CSS = _APP_CONFIG_ASSETS.pop("extra_css", None) or defaults.EXTRA_CSS

JS = [j for j in defaults.BUILT_IN_JS + EXTRA_JS if j]

CSS = [c for c in defaults.BUILT_IN_CSS + EXTRA_CSS if c]

# }}}

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

JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS = _APP_CONFIG.get(
    "jquery_file_upload_ui_options",
    defaults.JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS
)

JQUERY_FILE_UPLOAD_UI_DEFAULT_SORTABLE_OPTIONS = _APP_CONFIG.get(
    "jquery_file_upload_ui_sortable_options",
    defaults.JQUERY_FILE_UPLOAD_UI_DEFAULT_SORTABLE_OPTIONS
)

BOOTSTRAP_VERSION = _APP_CONFIG.get(
    "bootstrap_version", defaults.DEFAULT_BOOTSTRAP_VERSION)

JQUERY_LOCATION = (
        _APP_CONFIG_ASSETS.get("jquery")
        or defaults.DEFAULT_STATICS["jquery"])

BOOTSTRAP_CSS_LOCATION = (
        _APP_CONFIG_ASSETS.get("bootstrap_css")
        or defaults.DEFAULT_STATICS["bootstrap_css"][BOOTSTRAP_VERSION])

BOOTSTRAP_JS_LOCATION = (
        _APP_CONFIG_ASSETS.get("bootstrap_js")
        or defaults.DEFAULT_STATICS["bootstrap_js"][BOOTSTRAP_VERSION])
