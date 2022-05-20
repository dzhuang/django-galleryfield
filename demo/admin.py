from django import forms
from django.contrib import admin

from demo.models import DemoGallery
from galleryfield.mixins import GalleryFormMediaMixin
from galleryfield.models import BuiltInGalleryImage


class DemoGalleryAdminForm(GalleryFormMediaMixin, forms.ModelForm):
    class Meta:
        model = DemoGallery
        exclude = ()


class DemoGalleryAdmin(admin.ModelAdmin):
    form = DemoGalleryAdminForm


admin.site.register(DemoGallery, DemoGalleryAdmin)
admin.site.register(BuiltInGalleryImage)
