from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from gallery.fields import GalleryField


class DemoGallery(models.Model):
    images = GalleryField(verbose_name=_('Photos'), blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True,
        verbose_name=_('Owner'), on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('gallery-update', kwargs={'pk': self.pk})


class MyImageModel(models.Model):
    # A demo of target Image Model with get_image_field classmethod
    photo = models.ImageField()

    @classmethod
    def get_image_field(cls):
        return cls._meta.get_field("photo")
