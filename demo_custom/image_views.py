from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_sendfile import sendfile

from demo_custom.models import CustomImage
from galleryfield.image_views import (ImageCreateView, ImageCropView,
                                      ImageListView)


class CustomImageCreateView(LoginRequiredMixin, ImageCreateView):
    target_model = "demo_custom.CustomImage"
    disable_server_side_crop = False

    def create_instance_from_form(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()


class CustomImageListView(LoginRequiredMixin, ImageListView):
    target_model = "demo_custom.CustomImage"
    disable_server_side_crop = False

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class CustomImageCropView(LoginRequiredMixin, ImageCropView):
    target_model = "demo_custom.CustomImage"
    disable_server_side_crop = False

    def create_cropped_instance_from_form(self, form):
        self.object: CustomImage = form.save(commit=False)
        self.object.save()


# {{{ sendfile


@login_required
def image_download(request, **kwargs):
    user_id = kwargs["user_id"]  # noqa
    photo_id = kwargs["image_id"]
    file_name = kwargs["file_name"]  # noqa

    from demo_custom.models import CustomImage

    download_object = get_object_or_404(CustomImage, pk=photo_id)

    privilege = False

    if request.user.is_staff:
        privilege = True

    return _auth_download(request, download_object, privilege)


@login_required
def _auth_download(request, download_object, privilege=False):
    if request.user == download_object.user or privilege:
        return sendfile(request, download_object.photo.path)

    raise PermissionDenied(_("may not view other user's image"))

# }}}
