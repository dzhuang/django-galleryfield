from django.core.exceptions import PermissionDenied
from django.views.generic import CreateView, UpdateView
from django.views.generic.list import BaseListView

from galleryfield.mixins import (BaseCreateMixin, BaseCropViewMixin,
                                 BaseListViewMixin)


class ImageCreateView(BaseCreateMixin, CreateView):
    """
    The Class-based view handling the saving of uploaded image.

    .. attribute:: target_model

       |view_target_model|

    .. attribute:: crop_url_name

       |view_crop_url_name|

    .. attribute:: disable_server_side_crop

       |view_disable_server_side_crop|

    .. automethod:: form_valid
    """
    def form_valid(self, form):
        """User should override this method to save the object,
        for example, image model usually has a non-null user field,
        that should be handled here.

        See `the-save-method <https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#the-save-method>`_
        for detail.

        See :class:`galleryfield.image_views.BuiltInImageCreateView` for example.
        """  # noqa
        self.object.save()
        return super().form_valid(form)


class ImageListView(BaseListViewMixin, BaseListView):
    """
    The Class-based view for fetching the existing images of the gallery instance.

    .. attribute:: target_model

       |view_target_model|

    .. attribute:: crop_url_name

       |view_crop_url_name|

    .. attribute:: disable_server_side_crop

       |view_disable_server_side_crop|

    .. automethod:: get_queryset
    """
    def get_queryset(self):
        """
        User need to override this method to do some basic filter in terms of
        who can see which images.

        :return: A Queryset
        """
        return super().get_queryset()


class ImageCropView(BaseCropViewMixin, UpdateView):
    """
    The Class-based view handling server side cropping of an image model
    instance.

    .. attribute:: target_model

       |view_target_model|

    .. attribute:: crop_url_name

       |view_crop_url_name|

    .. attribute:: disable_server_side_crop

       |view_disable_server_side_crop|

    .. automethod:: form_valid
    """
    def form_valid(self, form):
        """Save the object from the form. This method should only be overridden
        when the model contains dynamic fields which need to be updated. For
        example, when there is a  ``DateTimeField`` which records the updated
        datetime of the image.
        """
        self.object = form.save()
        return super().form_valid(form)


class BuiltInImageCreateView(ImageCreateView):
    target_model = "galleryfield.BuiltInGalleryImage"
    crop_url_name = "galleryfield-builtingalleryimage-crop"  # Can be omitted
    disable_server_side_crop = False

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        return super().form_valid(form)


class BuiltInImageListView(ImageListView):
    target_model = "galleryfield.BuiltInGalleryImage"
    crop_url_name = "galleryfield-builtingalleryimage-crop"  # Can be omitted
    disable_server_side_crop = False

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(creator=self.request.user)
        return queryset


class BuiltInImageCropView(ImageCropView):
    target_model = "galleryfield.BuiltInGalleryImage"
    crop_url_name = "galleryfield-builtingalleryimage-crop"  # Can be commented
    disable_server_side_crop = False

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        if not self.request.user.is_superuser and obj.creator != self.request.user:
            raise PermissionDenied("May not crop other people's image")
        return obj
