JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS = {
    "autoUpload": False,
    "imageMaxWidth": 1024,
    "imageMaxHeight": 1024,
    "loadImageFileTypes": r"/^image\/(gif|jpeg|png|bmp|svg\+xml)$/",
    "sequentialUploads": True,
    "acceptFileTypes": r"/(\.|\/)(png|gif|bmp|jpe?g)$/i",
    "imageOrientation": True,
    "maxFileSize": 1.5 * 1024 ** 2,  # 1.5Mb
    "minFileSize": 0.0001 * 1024 ** 2,  # 0.0001Mb
    "disableImageResize": "/Android(?!.*Chrome)|Opera/.test(window.navigator "
                          "&& navigator.userAgent)",
}
"""dict: The default options for jQuery-File-Upload module in jQuery file upload UI.
"""


JQUERY_FILE_UPLOAD_UI_DEFAULT_SORTABLE_OPTIONS = {
    "disabled": False,
    "delay": 300,
    "animation": 200,
}
"""dict: The default options for SortableJS used in jQuery file upload UI. See
https://github.com/SortableJS/Sortable#options for details.
"""


# {{{ DO NOT change this if you have deployed this app on you production server!
# Or else it might cause unexpected result!

DEFAULT_UPLOAD_URL_NAME = "galleryfield-builtingalleryimage-upload"
DEFAULT_CROP_URL_NAME = "galleryfield-builtingalleryimage-crop"
DEFAULT_FETCH_URL_NAME = "galleryfield-builtingalleryimage-fetch"

DEFAULT_TARGET_IMAGE_MODEL = "galleryfield.BuiltInGalleryImage"
DEFAULT_TARGET_IMAGE_FIELD_NAME = "image"
DEFAULT_CREATOR_FIELD_NAME = "creator"

# }}}

BUILT_IN_JS = ["js/galleryfield-ui.js"]
BUILT_IN_CSS = []

EXTRA_JS = []
EXTRA_CSS = []

DEFAULT_THUMBNAIL_SIZE = "120x120"
DEFAULT_THUMBNAIL_QUALITY = 80

WIDGET_HIDDEN_INPUT_CSS_CLASS = "django-galleryfield"

PROMPT_ALERT_ON_WINDOW_RELOAD_IF_CHANGED = True

DEFAULT_BOOTSTRAP_VERSION = 3

_BOOTSTRAP_CSS_PATTERN = (
    "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/"
    "{}/css/bootstrap.min.css")

_BOOTSTRAP_JS_PATTERN = (
    "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/"
    "{}/js/bootstrap.min.js")

_JQUERY_LOCATION = (
    "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js")

DEFAULT_STATICS = {
    "jquery": _JQUERY_LOCATION,
    "bootstrap_css": {3: _BOOTSTRAP_CSS_PATTERN.format("3.4.1"),
                      4: _BOOTSTRAP_CSS_PATTERN.format("4.6.1"),
                      5: _BOOTSTRAP_CSS_PATTERN.format("5.1.3"),
                      },
    "bootstrap_js": {3: _BOOTSTRAP_JS_PATTERN.format("3.4.1"),
                     4: _BOOTSTRAP_JS_PATTERN.format("4.6.1"),
                     5: _BOOTSTRAP_JS_PATTERN.format("5.1.3")},
}
