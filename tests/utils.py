import shutil
import os
from django.conf import settings


def get_upload_directory():
    # "images" is the upload_to of image field in BuiltInGalleryImage model
    return os.path.join(settings.MEDIA_ROOT, "images")


def remove_upload_directory():
    # Avoid failing the use case where django append a hash to the file name
    # to prevent file collisions
    shutil.rmtree(get_upload_directory(), ignore_errors=True)
