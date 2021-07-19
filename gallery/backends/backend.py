import os

from django.urls import reverse
from sorl.thumbnail import get_thumbnail
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied

from gallery.conf import DEFAULT_THUMBNAIL_QUALITY


class BackendBase:
    def __init__(self, file_object, request=None, *args, **kwargs):
        self.request = request
        self.file_object = file_object
        self.request_args = args
        self.request_kwargs = kwargs
        self._saved = False

    def has_view_permission(self):
        return True

    def has_edit_permission(self):
        return True

    def has_delete_permission(self):
        return True

    def save(self):
        raise NotImplemented

    def get_image_size(self):
        raise NotImplemented

    @property
    def size(self):
        if not self.has_view_permission():
            raise PermissionDenied()
        if not self._saved:
            self.save()
        return self.get_image_size()

    def get_image_url(self):
        raise NotImplemented

    @property
    def url(self):
        if not self.has_view_permission():
            raise PermissionDenied()
        if not self._saved:
            self.save()
        return self.get_image_url()

    def get_image_file_name(self):
        raise NotImplemented

    @property
    def name(self):
        if not self.has_view_permission():
            raise PermissionDenied()
        if not self._saved:
            self.save()
        return self.get_image_file_name()

    def _get_thumbnail_url(self, preview_size):
        raise NotImplemented

    def get_thumbnail_url(self, preview_size):
        if not self.has_view_permission():
            raise PermissionDenied()
        if not self._saved:
            self.save()
        return self._get_thumbnail_url(preview_size)

    def get_delete_url(self):
        raise NotImplemented

    @property
    def delete_url(self):
        if not self.has_delete_permission():
            raise PermissionDenied()
        if not self._saved:
            self.save()
        return "javascript:void(0)"

    def get_crop_url(self):
        raise NotImplemented

    @property
    def crop_url(self):
        if not self.has_edit_permission():
            raise PermissionDenied()
        if not self._saved:
            self.save()
        return self.get_crop_url()


class BackendWithThumbnailField(BackendBase):
    def __init__(self, model, image_field_name, file_object, request=None, *args, **kargs):
        super().__init__(file_object, request, *args, **kargs)

        from gallery.conf import DEFAULT_CROP_URL_NAME
        self.crop_url_name = DEFAULT_CROP_URL_NAME

        from django.apps import apps as django_apps
        try:
            self.model = django_apps.get_model(model, require_ready=False)
        except Exception as e:
            raise e
        assert self.model is not None

        self.image_field_name = image_field_name

        self.instance = None
        self._saved = False

    def has_view_permission(self):
        if hasattr(self.instance, "creator"):
            return (self.instance.creator == self.request.user
                    or self.request.user.is_superuser())
        return True

    def has_delete_permission(self):
        if hasattr(self.instance, "creator"):
            return (self.instance.creator == self.request.user
                    or self.request.user.is_superuser())
        return True

    def has_edit_permission(self):
        if hasattr(self.instance, "creator"):
            return (self.instance.creator == self.request.user
                    or self.request.user.is_superuser())
        return True

    def get_extra_model_save_kwargs(self):  # noqa
        # This method could be overridden if more fields need to be saved.
        return {"creator": self.request.user}

    def save(self):
        if self._saved:
            return
        save_kwargs = {self.image_field_name: self.file_object}
        save_kwargs.update(self.get_extra_model_save_kwargs())

        instance = self.model.objects.create(**save_kwargs)

        self._saved = True
        self.instance = instance

    def get_image_size(self):
        return self.file_object.size

    def get_image_url(self):
        if not self._saved:
            self.save()
        return self.instance.image.url

    def get_image_file_name(self):
        if not self._saved:
            self.save()
        return os.path.basename(self.instance.image.path)

    def _get_thumbnail_url(self, preview_size):
        if not self._saved:
            self.save()

        return get_thumbnail(
            self.instance.image,
            "%sx%s" % (preview_size, preview_size),
            crop="center", quality=DEFAULT_THUMBNAIL_QUALITY).url

    def get_crop_url(self):
        if not self._saved:
            self.save()
        return reverse(self.crop_url_name, kwargs={'pk': self.instance.pk})

    @property
    def pk(self):
        if not self._saved:
            self.save()
        return self.instance.pk
