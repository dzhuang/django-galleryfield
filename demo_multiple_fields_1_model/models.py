from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from PIL import Image

from galleryfield.fields import GalleryField


def fileName(image):
    file_url = list(image.url.split("/"))
    file_url.reverse()
    file_name = file_url[0].split(".")[0]
    return file_name


class MyImage1(models.Model):
    photo1 = models.ImageField(
        upload_to="my_images1", storage=default_storage, verbose_name=_("Image1")
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=False,
        verbose_name=_("Creator"),
        on_delete=models.CASCADE,
    )

    @classmethod
    def get_image_field(cls):
        return cls._meta.get_field("photo1")


class MyImage2(models.Model):
    photo2 = models.ImageField(
        upload_to="my_images2", storage=default_storage, verbose_name=_("Image2")
    )

    @classmethod
    def get_image_field(cls):
        return cls._meta.get_field("photo2")


class MyGallery(models.Model):
    album1 = GalleryField(
        target_model="demo_multiple_fields_1_model.MyImage1",
        verbose_name=_("My photos"))
    album2 = GalleryField(
        target_model="demo_multiple_fields_1_model.MyImage2",
        verbose_name=_("My photos2"))
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=False,
        verbose_name=_("Owner"),
        on_delete=models.CASCADE,
    )
