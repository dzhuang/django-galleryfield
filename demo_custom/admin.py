from django import forms
from django.contrib import admin

from demo.admin import GalleryAdminFormMixin
from demo_custom.models import CustomDemoGallery, CustomImage


class CustomDemoGalleryAdminForm(GalleryAdminFormMixin, forms.ModelForm):
    class Meta:
        model = CustomDemoGallery
        exclude = ()


class CustomDemoGalleryAdmin(admin.ModelAdmin):
    form = CustomDemoGalleryAdminForm


admin.site.register(CustomDemoGallery, CustomDemoGalleryAdmin)
admin.site.register(CustomImage)
