from django.contrib import admin

from . import models

admin.site.register(models.DemoGallery)
admin.site.register(models.DemoGalleryImage)
