GALLERY_WIDGET_UI_DEFAULT_OPTIONS = {
    "autoUpload": "false",
    "imageMaxWidth": 1024,
    "imageMaxHeight": 1024,
    "loadImageFileTypes": r"/^image\/(gif|jpeg|png|bmp|svg\+xml)$/",
    "sequentialUploads": "true",
    "acceptFileTypes": r"/(\.|\/)(png|gif|bmp|jpe?g)$/i",
    "imageOrientation": "true",
    "maxNumberOfFiles": 0,
    "previewMaxWidth": 80,
    "previewMaxHeight": 80,
    "maxFileSize": 1.5 * 1024 ** 2,  # 1.5Mb
    "minFileSize": 0.0001 * 1024 ** 2,  # 0.0001Mb
    "disableImageResize": "/Android(?!.*Chrome)|Opera/.test(window.navigator && navigator.userAgent)",
}

DEFAULT_UPLOAD_HANDLER_URL_NAME = "gallery_image_upload"
DEFAULT_CROP_URL_NAME = "gallery_image_crop"

DEFAULT_TARGET_IMAGE_MODEL = "gallery.BuiltInGalleryImage"
DEFAULT_TARGET_IMAGE_FIELD_NAME = "image"
DEFAULT_CREATOR_FIELD_NAME = "creator"

BOOTSTRAP_JS_PATH = 'vendor/bootstrap/dist/js/bootstrap.min.js'
BOOTSTRAP_CSS_PATH = 'vendor/bootstrap/dist/css/bootstrap.min.css'
JQUERY_JS_PATH = "vendor/jquery.min.js"
EXTRA_JS = []
EXTRA_CSS = []

DEFAULT_THUMBNAIL_SIZE = 120
DEFAULT_THUMBNAIL_QUALITY = 80

OLD_VALUE_STR = 'old_%s_value'
DELETED_VALUE_STR = 'deleted_%s_value'

WIDGET_HIDDEN_INPUT_CSS_CLASS = "django-gallery-widget"

PROMPT_ALERT_ON_WINDOW_RELOAD_IF_CHANGED = True
