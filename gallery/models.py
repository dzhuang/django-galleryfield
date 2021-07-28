import os
from django.db import models
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from sorl.thumbnail import get_thumbnail
from django.urls import reverse


from gallery.conf import (
    DEFAULT_CROP_URL_NAME, DEFAULT_THUMBNAIL_QUALITY, DEFAULT_THUMBNAIL_SIZE)


class BuiltInGalleryImage(models.Model):
    image = models.ImageField(
        upload_to="images", storage=default_storage, verbose_name=_("Image"))
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=False, blank=False,
        verbose_name=_('Creator'), on_delete=models.CASCADE)

    @classmethod
    def get_image_field(cls):
        return cls._meta.get_field("image")

    def get_owner(self):
        return self.creator

    @property
    def owner(self):
        return self.creator

    @property
    def size(self):
        return self.image.size

    @property
    def url(self):
        return self.image.url

    @property
    def name(self):
        return os.path.basename(self.image.path)

    def get_thumbnail_url(self, preview_size=None):
        preview_size = preview_size or DEFAULT_THUMBNAIL_SIZE
        return get_thumbnail(self.image,
                             "%sx%s" % (preview_size, preview_size),
                             crop="center", quality=DEFAULT_THUMBNAIL_QUALITY).url

    @property
    def delete_url(self):
        return "javascript:void(0)"

    @property
    def crop_url(self):
        return reverse(
            DEFAULT_CROP_URL_NAME, kwargs={'pk': self.pk})

    def has_view_permission(self, request):
        return True

    def has_edit_permission(self, request):
        return self.creator == request.user or request.user.is_superuser

    def has_delete_permission(self, request):
        return self.creator == request.user or request.user.is_superuser

    def serialized(self, preview_size=None):
        return {
            'pk': self.pk,
            'name': self.name,
            'size': self.size,
            'url': self.url,
            'thumbnailUrl': self.get_thumbnail_url(preview_size),
            'deleteUrl': self.delete_url,

            # todo: not implemented
            # 'cropurl': file_wrapper.crop_url,
        }
