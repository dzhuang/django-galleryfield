JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS = {
    "autoUpload": False,
    "imageMaxWidth": 1024,
    "imageMaxHeight": 1024,
    "loadImageFileTypes": r"/^image\/(gif|jpeg|png|bmp|svg\+xml)$/",
    "sequentialUploads": "true",
    "acceptFileTypes": r"/(\.|\/)(png|gif|bmp|jpe?g)$/i",
    "imageOrientation": True,
    "maxFileSize": 1.5 * 1024 ** 2,  # 1.5Mb
    "minFileSize": 0.0001 * 1024 ** 2,  # 0.0001Mb
    "disableImageResize": "/Android(?!.*Chrome)|Opera/.test(window.navigator "
                          "&& navigator.userAgent)",
}
"""dict: The default options for jQuery-File-Upload module.
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

# BE CAUTIOUS: changing the sequence of the assets
# might result in failure to render the widget

VENDER_JS_NAMES = (
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

VENDER_CSS_NAMES = (
    'bootstrap.css',
    'jquery-ui.theme.css',
    'jquery.fileupload.css',
    'jquery.fileupload-ui.css',
    'blueimp-gallery.css',
    'blueimp-gallery-indicator.css',
    'font-awesome.css',
    'cropper.css')

DEFAULT_ASSETS = {
    # js assets
    "jquery.js": "jquery/dist/jquery.min.js",
    "jquery-ui.js": "jquery-ui-dist/jquery-ui.min.js",
    "jquery.ui.widget.min.js":
        "blueimp-file-upload/js/vendor/jquery.ui.widget.js",
    "blueimp-tmpl.js":
        "blueimp-tmpl/js/tmpl.min.js",
    "load-image.all.min.js":
        "blueimp-load-image/js/load-image.all.min.js",
    "blueimp-canvas-to-blob.js":
        "blueimp-canvas-to-blob/js/canvas-to-blob.min.js",
    "bootstrap.js":
        "bootstrap/dist/js/bootstrap.min.js",
    "jquery.iframe-transport.js":
        "blueimp-file-upload/js/jquery.iframe-transport.js",
    "jquery.fileupload.js": "blueimp-file-upload/js/jquery.fileupload.js",
    "jquery.fileupload-process.js":
        "blueimp-file-upload/js/jquery.fileupload-process.js",
    "jquery.fileupload-image.js":
        "blueimp-file-upload/js/jquery.fileupload-image.js",
    "jquery.fileupload-audio.js":
        "blueimp-file-upload/js/jquery.fileupload-audio.js",
    "jquery.fileupload-video.js":
        "blueimp-file-upload/js/jquery.fileupload-video.js",
    "jquery.fileupload-validate.js":
        "blueimp-file-upload/js/jquery.fileupload-validate.js",
    "jquery.fileupload-ui.js":
        "blueimp-file-upload/js/jquery.fileupload-ui.js",
    "jquery.blueimp-gallery.js":
        "blueimp-gallery/js/jquery.blueimp-gallery.min.js",
    "blueimp-gallery-fullscreen.js":
        "blueimp-gallery/js/blueimp-gallery-fullscreen.js",
    "blueimp-gallery-indicator.js":
        "blueimp-gallery/js/blueimp-gallery-indicator.js",
    "cropper.js": "cropper/dist/cropper.min.js",

    # css assets
    "bootstrap.css": "bootstrap/dist/css/bootstrap.min.css",
    "jquery-ui.theme.css": "jquery-ui-dist/jquery-ui.theme.min.css",
    "jquery.fileupload.css": "blueimp-file-upload/css/jquery.fileupload.css",
    "jquery.fileupload-ui.css":
        "blueimp-file-upload/css/jquery.fileupload-ui.css",
    "blueimp-gallery.css": "blueimp-gallery/css/blueimp-gallery.min.css",
    "blueimp-gallery-indicator.css":
        "blueimp-gallery/css/blueimp-gallery-indicator.css",
    "font-awesome.css": "font-awesome/css/font-awesome.min.css",
    "cropper.css": "cropper/dist/cropper.min.css",
}
"""dict: The default assets used to render the :class:`GalleryWidget` instance.
"""

BUILT_IN_JS = ["js/jquery.fileupload-ui-gallery-widget.js"]
BUILT_IN_CSS = []

EXTRA_JS = []
EXTRA_CSS = []

DEFAULT_THUMBNAIL_SIZE = "120x120"
DEFAULT_THUMBNAIL_QUALITY = 80

WIDGET_HIDDEN_INPUT_CSS_CLASS = "django-galleryfield"

PROMPT_ALERT_ON_WINDOW_RELOAD_IF_CHANGED = True
