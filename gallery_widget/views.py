from django.core.exceptions import PermissionDenied
from django.views.generic import CreateView, UpdateView
from django.views.generic.list import BaseListView

from gallery_widget.mixins import (BaseCreateMixin, BaseCropViewMixin,
                                   BaseListViewMixin)


class ImageCreateView(BaseCreateMixin, CreateView):
    def form_valid(self, form):
        """User should override this method to save the object,
        for example, image model usually has a not null user field,
        that should be handled here.

        See https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/#the-save-method
        for detail.

        See :class:`gallery_widget.views.BuiltInImageCreateView` for example.
        """  # noqa
        self.object.save()
        return super().form_valid(form)


class ImageListView(BaseListViewMixin, BaseListView):
    def get_queryset(self):
        """
        You need to override this method to do some basic
        filter in terms of who can see which images.
        :return: A Queryset
        """
        return super().get_queryset()


class ImageCropView(BaseCropViewMixin, UpdateView):
    def form_valid(self, form):
        """This method should be overridden to save the object,
        if only the model contains dynamic fields like DateTimeField
        """
        self.object = form.save()
        return super().form_valid(form)


class BuiltInImageCreateView(ImageCreateView):
    target_model = "gallery_widget.BuiltInGalleryImage"
    crop_url_name = "builtingalleryimage-crop"
    disable_server_side_crop = False

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        return super().form_valid(form)


class BuiltInImageListView(ImageListView):
    target_model = "gallery_widget.BuiltInGalleryImage"
    crop_url_name = "builtingalleryimage-crop"
    disable_server_side_crop = False

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(creator=self.request.user)
        return queryset


class BuiltInImageCropView(ImageCropView):
    target_model = "gallery_widget.BuiltInGalleryImage"
    crop_url_name = "builtingalleryimage-crop"
    disable_server_side_crop = False

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        if not self.request.user.is_superuser and obj.creator != self.request.user:
            raise PermissionDenied("May not crop other people's image")
        return obj
