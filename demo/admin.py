from django.contrib import admin

from demo.models import DemoGallery
from galleryfield.models import BuiltInGalleryImage

admin.site.register(DemoGallery)
admin.site.register(BuiltInGalleryImage)
