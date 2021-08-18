from django.contrib import admin

from demo.models import DemoGallery
from gallery_widget.models import BuiltInGalleryImage

admin.site.register(DemoGallery)
admin.site.register(BuiltInGalleryImage)
