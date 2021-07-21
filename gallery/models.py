import os
from django.db import models
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from sorl.thumbnail import get_thumbnail
from django.urls import reverse


from gallery.conf import (
    DEFAULT_CROP_URL_NAME, DEFAULT_THUMBNAIL_QUALITY, DEFAULT_THUMBNAIL_SIZE)


class ImageBaseModel(models.Model):
    class Meta:
        abstract = True

    @property
    def image_field_name(self):
        raise NotImplemented

    @property
    def creator_field_name(self):
        raise NotImplemented

    def has_view_permission(self, request):
        raise NotImplemented

    def has_edit_permission(self, request):
        raise NotImplemented

    def has_delete_permission(self, request):
        raise NotImplemented

    @property
    def size(self):
        return getattr(self, self.image_field_name).size

    @property
    def url(self):
        return getattr(self, self.image_field_name).url

    @property
    def name(self):
        return os.path.basename(
            getattr(self, self.image_field_name).path)

    def get_thumbnail_url(self, preview_size=None):
        preview_size = preview_size or DEFAULT_THUMBNAIL_SIZE
        return get_thumbnail(
            getattr(self, self.image_field_name),
            "%sx%s" % (preview_size, preview_size),
            crop="center", quality=DEFAULT_THUMBNAIL_QUALITY).url

    @property
    def delete_url(self):
        return "javascript:void(0)"

    @property
    def crop_url(self):
        return reverse(
            DEFAULT_CROP_URL_NAME, kwargs={'pk': self.pk})


class BuiltInGalleryImage(ImageBaseModel):
    image = models.ImageField(
        upload_to="images", storage=default_storage, verbose_name=_("Image"))
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=False, blank=False,
        verbose_name=_('Creator'), on_delete=models.CASCADE)

    @property
    def image_field_name(self):
        return "image"

    @property
    def creator_field_name(self):
        return "creator"

    def has_view_permission(self, request):
        return True

    def has_edit_permission(self, request):
        return self.creator == request.user or request.user.is_superuser

    def has_delete_permission(self, request):
        return self.creator == request.user or request.user.is_superuser
