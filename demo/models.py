from django.db import models
from django.urls import reverse
from gallery.fields import GalleryField


class DemoGallery(models.Model):
    images = GalleryField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('gallery-update', kwargs={'pk': self.pk})
