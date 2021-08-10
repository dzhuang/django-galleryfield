from django.core.exceptions import PermissionDenied


from gallery.mixins import ImageCreateView, ImageListView, ImageCropView


class BuiltInImageCreateView(ImageCreateView):
    target_model = "gallery.BuiltInGalleryImage"
    crop_url_name = "builtingalleryimage_crop"
    disable_server_side_crop = False

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        return super().form_valid(form)


class BuiltInImageListView(ImageListView):
    target_model = "gallery.BuiltInGalleryImage"
    crop_url_name = "builtingalleryimage_crop"
    disable_server_side_crop = False

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(creator=self.request.user)
        return queryset


class BuiltInImageCropView(ImageCropView):
    target_model = "gallery.BuiltInGalleryImage"
    crop_url_name = "builtingalleryimage_crop"
    disable_server_side_crop = False

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        if not self.request.user.is_superuser and obj.creator != self.request.user:
            raise PermissionDenied("May not crop other people's image")
        return obj
