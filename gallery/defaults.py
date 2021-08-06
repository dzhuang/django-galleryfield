GALLERY_WIDGET_UI_DEFAULT_OPTIONS = {
    "autoUpload": "false",
    "imageMaxWidth": 1024,
    "imageMaxHeight": 1024,
    "loadImageFileTypes": r"/^image\/(gif|jpeg|png|bmp|svg\+xml)$/",
    "sequentialUploads": "true",
    "acceptFileTypes": r"/(\.|\/)(png|gif|bmp|jpe?g)$/i",
    "imageOrientation": "true",
    # "maxNumberOfFiles": 0,  # This is overridden by GalleryFormField max_number_of_images value  # noqa
    # "previewMaxWidth": 80,  # This is overridden by DEFAULT_THUMBNAIL_SIZE
    # "previewMaxHeight": 80,
    "maxFileSize": 1.5 * 1024 ** 2,  # 1.5Mb
    "minFileSize": 0.0001 * 1024 ** 2,  # 0.0001Mb
    "disableImageResize": "/Android(?!.*Chrome)|Opera/.test(window.navigator "
                          "&& navigator.userAgent)",
}

# {{{ DO NOT change this if you have deployed this app on you production server!
# Or else it might cause unexpected result!

DEFAULT_UPLOAD_HANDLER_URL_NAME = "gallery_image_upload"
DEFAULT_CROP_URL_NAME = "gallery_image_crop"
DEFAULT_FETCH_URL_NAME = "gallery_images_fetch"

DEFAULT_TARGET_IMAGE_MODEL = "gallery.BuiltInGalleryImage"
DEFAULT_TARGET_IMAGE_FIELD_NAME = "image"
DEFAULT_CREATOR_FIELD_NAME = "creator"

# }}}

DEFAULT_ASSETS = {
    # js assets
    "jquery.js": "vendor/jquery.min.js",
    "jquery-ui.js": "vendor/jquery-ui-dist/jquery-ui.min.js",
    "jquery.ui.widget.min.js": "vendor/blueimp-file-upload/js/vendor/jquery.ui.widget.js",
    "blueimp-tmpl.js": "vendor/blueimp-tmpl/js/tmpl.min.js",
    "load-image.all.min.js": "vendor/blueimp-load-image/js/load-image.all.min.js",
    "blueimp-canvas-to-blob.js": "vendor/blueimp-canvas-to-blob/js/canvas-to-blob.js",
    "bootstrap.js": "vendor/bootstrap/dist/js/bootstrap.min.js",
    "jquery.iframe-transport.js": "vendor/jquery.iframe-transport/jquery.iframe-transport.js",
    "jquery.fileupload.js": "vendor/blueimp-file-upload/js/jquery.fileupload.js",
    "jquery.fileupload-process.js": "vendor/blueimp-file-upload/js/jquery.fileupload-process.js",
    "jquery.fileupload-image.js": "vendor/blueimp-file-upload/js/jquery.fileupload-image.js",
    "jquery.fileupload-audio.js": "vendor/blueimp-file-upload/js/jquery.fileupload-audio.js",
    "jquery.fileupload-video.js": "vendor/blueimp-file-upload/js/jquery.fileupload-video.js",
    "jquery.fileupload-validate.js": "vendor/blueimp-file-upload/js/jquery.fileupload-validate.js",
    "jquery.fileupload-ui.js": "vendor/blueimp-file-upload/js/jquery.fileupload-ui.js",
    "jquery.blueimp-gallery.js": "vendor/blueimp-gallery/js/jquery.blueimp-gallery.min.js",
    "blueimp-gallery-indicator.js": "vendor/blueimp-gallery/js/blueimp-gallery-indicator.js",
    "cropper.js": "vendor/cropper/dist/cropper.min.js",

    # css assets
    "bootstrap.css": "vendor/bootstrap/dist/css/bootstrap.min.css",
    "jquery-ui.theme.css": "vendor/jquery-ui-dist/jquery-ui.theme.min.css",
    "jquery.fileupload.css": "vendor/blueimp-file-upload/css/jquery.fileupload.css",
    "jquery.fileupload-ui.css": "vendor/blueimp-file-upload/css/jquery.fileupload-ui.css",
    "blueimp-gallery.css": "vendor/blueimp-gallery/css/blueimp-gallery.min.css",
    "blueimp-gallery-indicator.css": "vendor/blueimp-gallery/css/blueimp-gallery-indicator.css",
    "font-awesome.css": "vendor/font-awesome/css/font-awesome.min.css",
    "cropper.css": "vendor/cropper/dist/cropper.min.css",
}

BOOTSTRAP_JS_PATH = "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"
BOOTSTRAP_CSS_PATH = "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
JQUERY_JS_PATH = "https://code.jquery.com/jquery-3.6.0.min.js"

EXTRA_JS = []
EXTRA_CSS = []

DEFAULT_THUMBNAIL_SIZE = 120
DEFAULT_THUMBNAIL_QUALITY = 80

OLD_VALUE_STR = 'old_%s_value'
DELETED_VALUE_STR = 'deleted_%s_value'

WIDGET_HIDDEN_INPUT_CSS_CLASS = "django-gallery-widget"

PROMPT_ALERT_ON_WINDOW_RELOAD_IF_CHANGED = True
