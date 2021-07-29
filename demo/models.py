from django.db import models
from django.urls import reverse
from gallery.fields import GalleryField
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class DemoGallery(models.Model):
    images = GalleryField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('gallery-update', kwargs={'pk': self.pk})
