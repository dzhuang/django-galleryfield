from django.core.exceptions import PermissionDenied

from galleryfield.image_views import (ImageCreateView, ImageCropView,
                                      ImageListView)


class MyImage1CreateView(ImageCreateView):
    target_model = "demo_multiple_fields_1_model.MyImage1"
    disable_server_side_crop = False

    def create_instance_from_form(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()


class MyImage1ListView(ImageListView):
    target_model = "demo_multiple_fields_1_model.MyImage1"
    disable_server_side_crop = False

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(creator=self.request.user)
        return queryset


class MyImage1CropView(ImageCropView):
    target_model = "demo_multiple_fields_1_model.MyImage1"
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


class MyImage2CreateView(ImageCreateView):
    target_model = "demo_multiple_fields_1_model.MyImage2"
    disable_server_side_crop = False

    def create_instance_from_form(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()


class MyImage2ListView(ImageListView):
    target_model = "demo_multiple_fields_1_model.MyImage2"
    disable_server_side_crop = False

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(creator=self.request.user)
        return queryset


class MyImage2CropView(ImageCropView):
    target_model = "demo_multiple_fields_1_model.MyImage2"
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
