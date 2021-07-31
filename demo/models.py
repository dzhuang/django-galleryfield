from django.db import models
from django.urls import reverse
from gallery.fields import GalleryField


class DemoGallery(models.Model):
    images = GalleryField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('gallery-update', kwargs={'pk': self.pk})


class MyImageModel(models.Model):
    # A demo of Image Model with get_image_field classmethod
    photo = models.ImageField()

    @classmethod
    def get_image_field(cls):
        return cls._meta.get_field("photo")
