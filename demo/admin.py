from django.contrib import admin

from . import models
from gallery_widget.models import BuiltInGalleryImage

admin.site.register(models.DemoGallery)
admin.site.register(BuiltInGalleryImage)
