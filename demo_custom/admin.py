from django import forms
from django.contrib import admin

from demo_custom.models import CustomDemoGallery, CustomImage
from galleryfield.mixins import GalleryFormMediaMixin


class CustomDemoGalleryAdminForm(GalleryFormMediaMixin, forms.ModelForm):
    class Meta:
        model = CustomDemoGallery
        exclude = ()


class CustomDemoGalleryAdmin(admin.ModelAdmin):
    form = CustomDemoGalleryAdminForm


admin.site.register(CustomDemoGallery, CustomDemoGalleryAdmin)
admin.site.register(CustomImage)
