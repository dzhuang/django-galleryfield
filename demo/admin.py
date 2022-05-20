from django import forms
from django.contrib import admin

from demo.models import DemoGallery
from galleryfield.models import BuiltInGalleryImage


class GalleryAdminFormMixin:
    class Media:
        css = {
            "all": ["https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.4.1/css/bootstrap.css"]  # noqa
        }

        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.4.1/js/bootstrap.min.js"  # noqa
        )


class DemoGalleryAdminForm(GalleryAdminFormMixin, forms.ModelForm):
    class Meta:
        model = DemoGallery
        exclude = ()


class DemoGalleryAdmin(admin.ModelAdmin):
    form = DemoGalleryAdminForm


admin.site.register(DemoGallery, DemoGalleryAdmin)
admin.site.register(BuiltInGalleryImage)
