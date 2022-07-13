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

    .. automethod:: create_instance_from_form
    """
    def form_valid(self, form):
        self.create_instance_from_form(form)
        return super().form_valid(form)

    def create_instance_from_form(self, form):
        """User should provide this method to save the object which will be used 
        in form_valid method. Typically, ``self.object`` is expected to be saved 
        here with  
        `the-save-method <https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#the-save-method>`_.

        See :class:`galleryfield.image_views.BuiltInImageCreateView` for example.
        """  # noqa

        raise NotImplementedError(
            'subclasses of ImageCreateView must provide '
            'a create_instance_from_form() method')


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
    instance. Note that a new image model instance will be created rather
    than updating the cropped instance.

    .. attribute:: target_model

       |view_target_model|

    .. attribute:: crop_url_name

       |view_crop_url_name|

    .. attribute:: disable_server_side_crop

       |view_disable_server_side_crop|

    .. automethod:: create_cropped_instance_from_form
    """
    def form_valid(self, form):
        """Save the object from the form. This method should only be overridden
        when the model contains dynamic fields which need to be updated. For
        example, when there is a  ``DateTimeField`` which records the updated
        datetime of the image.
        """
        self.create_cropped_instance_from_form(form)
        return super().form_valid(form)

    def create_cropped_instance_from_form(self, form):
        """User should provide this method to save the object which will be used 
        in form_valid method. Typically, self.object is expected to be saved 
        here with  
        `the-save-method <https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#the-save-method>`_.

        See :class:`galleryfield.image_views.BuiltInImageCropView` for example.
        
        Note that beside the id (pk) and image field, all other field values of the
        saved cropped instance will be the same with the original instance. You 
        need to set those values before calling ``self.object.save()`` method.
        
        """  # noqa

        raise NotImplementedError(
            'subclasses of ImageCropView must provide '
            'a create_cropped_instance_from_form() method')


class BuiltInImageCreateView(ImageCreateView):
    target_model = "galleryfield.BuiltInGalleryImage"
    crop_url_name = "galleryfield-builtingalleryimage-crop"  # Can be omitted
    disable_server_side_crop = False

    def create_instance_from_form(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()


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
            raise PermissionDenied("May not crop other user's image")
        return obj

    def create_cropped_instance_from_form(self, form):
        # we don't need to set self.object.creator here because
        # it's copied from the original instance.
        self.object = form.save()
