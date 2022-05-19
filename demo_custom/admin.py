from django.contrib import admin

from demo_custom.models import CustomDemoGallery, CustomImage

admin.site.register(CustomDemoGallery)
admin.site.register(CustomImage)
