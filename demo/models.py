from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from galleryfield.fields import GalleryField


class DemoGallery(models.Model):
    images = GalleryField(verbose_name=_('Photos'), blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True,
        verbose_name=_('Owner'), on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('gallery-update', kwargs={'pk': self.pk})
