from django import forms
from django.contrib import admin

from demo_multiple_fields_1_model.models import MyGallery
from galleryfield.mixins import GalleryFormMediaMixin


class MyGalleryAdminForm(GalleryFormMediaMixin, forms.ModelForm):
    class Meta:
        model = MyGallery
        exclude = ()


class MyGalleryAdmin(admin.ModelAdmin):
    form = MyGalleryAdminForm


admin.site.register(MyGallery, MyGalleryAdmin)

