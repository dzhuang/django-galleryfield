import os

from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class BackendBase:
    def __init__(self, file_object, request=None, *args, **kwargs):
        self.request = request
        self.file_object = file_object
        self.request_args = args
        self.request_kwargs = kwargs

    def save(self):
        raise NotImplemented

    def get_image_size(self):
        raise NotImplemented

    def get_image_url(self):
        raise NotImplemented

    def get_image_file_name(self):
        raise NotImplemented

    def get_thumbnail_url(self):
        raise NotImplemented

    def get_delete_url(self):
        raise NotImplemented


class BackendWithThumbnailField(BackendBase):
    def __init__(self, file_object, request=None, *args, **kargs):
        super().__init__(file_object, request, *args, **kargs)

        from gallery.registry import get_image_model
        from gallery.configs import GALLERY_DELETE_URL_NAME
        self.delete_url_name = GALLERY_DELETE_URL_NAME
        self.model = get_image_model()
        assert self.model is not None

        self.instance = None
        self._saved = False

    def get_extra_model_save_kwargs(self):  # noqa
        # This method could be overridden if more fields need to be saved.
        return {}

    def save(self):
        if self._saved:
            return
        save_kwargs = {"image": self.file_object}
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

    def get_thumbnail_url(self):
        if not self._saved:
            self.save()
        if hasattr(self.instance, "thumbnail") and hasattr(self.instance.thumbnail, "url"):
            return self.instance.thumbnail.url
        elif hasattr(self.instance, "get_thumbnail_url") and callable(self.instance.get_thumbnail_url):
            return self.instance.get_thumbnail_url()
        raise RuntimeError(_("No thumbnail url attribute or get_thumbnail_url method defined."))

    def get_delete_url(self):
        if not self._saved:
            self.save()
        return reverse(self.delete_url_name, kwargs={'pk': self.instance.pk})
