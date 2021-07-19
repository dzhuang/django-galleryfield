from django.contrib import admin

from . import models
from gallery.models import BuiltInGalleryImage

admin.site.register(models.DemoGallery)
admin.site.register(BuiltInGalleryImage)
