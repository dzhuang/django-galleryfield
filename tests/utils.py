import shutil
from django.conf import settings


def get_upload_directory():
    return settings.MEDIA_ROOT


def remove_upload_directory():
    # Called on test setup
    # Avoid falling in the use case chere django append a hash to the file name
    # to prevent file collisions
    shutil.rmtree(get_upload_directory(), ignore_errors=True)
