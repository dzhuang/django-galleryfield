from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from galleryfield.fields import GalleryField


class CustomDemoGallery(models.Model):
    """
    The gallery model used in demo_custom.

    """
    images = GalleryField(
        verbose_name=_('Photos'), target_model='demo_custom.CustomImage',
        blank=True, null=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True,
        verbose_name=_('Creator'), on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('custom-gallery-update', kwargs={'pk': self.pk})


@deconstructible
class UserImageStorage(FileSystemStorage):
    def __init__(self):
        super().__init__(location=settings.SENDFILE_ROOT)


storage = UserImageStorage()


def user_img_path(instance, filename):
    return "user_images/user_{}/{}".format(instance.user_id, filename)


class CustomImage(models.Model):
    photo = models.ImageField(
        upload_to=user_img_path, storage=storage, verbose_name=_("Photo"))

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=False, blank=False,
        verbose_name=_('Owner'), on_delete=models.CASCADE)

    added_at = models.DateTimeField(default=now)

    # This is used to determine where the image is an orphan
    gallery = models.ManyToManyField(
        CustomDemoGallery, blank=True,
        verbose_name=_("Gallery belongs to"), related_name="related_images")

    def get_image_url(self):
        import os
        file_name = os.path.basename(self.photo.path)

        return reverse(
            "image_download", args=[
                self.user_id,
                self.pk,
                file_name
            ])

    def get_crop_url(self):
        return reverse(
            "customimage-crop", args=[
                self.pk
            ])

    def serialize_extra(self, request):
        from django.utils import formats

        return {
            "added_datetime": formats.date_format(
                self.added_at, "SHORT_DATETIME_FORMAT")}

    @classmethod
    def get_image_field(cls):
        return cls._meta.get_field("photo")
