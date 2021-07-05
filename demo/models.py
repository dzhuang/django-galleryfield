from django.db import models
from django.urls import reverse
from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

from gallery.configs import GALLERY_THUMBNAIL_SIZE, GALLERY_THUMBNAIL_QUALITY
from gallery.fields import ImagesField


class DemoGalleryImage(models.Model):
    image = models.ImageField(upload_to="images", storage=default_storage)
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFit(*GALLERY_THUMBNAIL_SIZE)],
        format='PNG',
        options={'quality': GALLERY_THUMBNAIL_QUALITY})


class DemoGallery(models.Model):
    images = ImagesField()

    def get_absolute_url(self):
        return reverse('gallery-update', kwargs={'pk': self.pk})
