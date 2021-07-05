from django.conf import settings

JQUERY_JS_PATH = None
BOOTSTRAP_JS_PATH = None
BOOTSTRAP_CSS_PATH = None
if not getattr(settings, "DJANGO_GALLERY_ALREADY_LOADED_BOOTSTRAP", False):
    BOOTSTRAP_JS_PATH = getattr(
        settings, "DJANGO_GALLERY_BOOTSTRAP_JS_PATH", 'js/bootstrap.min.js')
    BOOTSTRAP_CSS_PATH = getattr(
        settings, "DJANGO_GALLERY_BOOTSTRAP_CSS_PATH",
        'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css')
    JQUERY_JS_PATH = getattr(settings, "DJANGO_GALLERY_JQUERY_JS_PATH", "js/jquery.min.js")

GALLERY_EXTRA_JS = getattr(settings, "DJANGO_GALLERY_EXTRA_JS", [])
GALLERY_EXTRA_CSS = getattr(settings, "DJANGO_GALLERY_EXTRA_CSS", [])

GALLERY_THUMBNAIL_SIZE = getattr(
    settings, "DJANGO_GALLERY_THUMBNAIL_SIZE", (70, 70))

GALLERY_THUMBNAIL_QUALITY = getattr(
    settings, "DJANGO_GALLERY_THUMBNAIL_QUALITY", 50)

_APP_CONFIG = getattr(settings, "DJANGO_GALLERY_APP")

GALLERY_DELETE_URL_NAME = _APP_CONFIG.get("DELETE_URL_NAME", "gallery_image_delete")
GALLERY_UPLOAD_HANDLER_URL_NAME = _APP_CONFIG.get("UPLOAD_HANDER_URL_NAME", "gallery_image_upload")

