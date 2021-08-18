from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models
from django.utils.translation import gettext_lazy as _


class BuiltInGalleryImage(models.Model):
    image = models.ImageField(
        upload_to="images", storage=default_storage, verbose_name=_("Image"))
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=False, blank=False,
        verbose_name=_('Creator'), on_delete=models.CASCADE)

    # This snippet will not run because we already have the ImageField named 'image'
    # @classmethod
    # def get_image_field(cls):
    #     return cls._meta.get_field("image")
