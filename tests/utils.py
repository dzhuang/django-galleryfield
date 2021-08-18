import os
import shutil
import tempfile

from django.conf import settings

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'resource')
test_media_root = os.path.join(tempfile.gettempdir(), "gallery_widget_media")


def get_upload_file_path(file_name, fixture_path=FIXTURE_PATH):
    return os.path.join(fixture_path, file_name)


def get_upload_directory():
    # "images" is the upload_to of image field in BuiltInGalleryImage model
    return os.path.join(settings.MEDIA_ROOT, "images")


def get_thumbnail_directory():
    # "images" is the upload_to of image field in BuiltInGalleryImage model
    return os.path.join(settings.MEDIA_ROOT, "cache")


def remove_upload_directory():
    # Avoid failing the use case where django append a hash to the file name
    # to prevent file collisions
    shutil.rmtree(get_upload_directory(), ignore_errors=True)
    shutil.rmtree(get_thumbnail_directory(), ignore_errors=True)
