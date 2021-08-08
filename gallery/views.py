import os
import json
from PIL import Image
from io import BytesIO
from urllib.parse import unquote

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.translation import gettext
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import CreateView
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile

from gallery.models import BuiltInGalleryImage
from gallery import conf
from gallery.utils import is_image, get_serialized_image, get_ordered_serialized_images
from gallery.mixins import ImageCreateMixin


class ImageCreateView(ImageCreateMixin, CreateView):
    target_model = "gallery.BuiltInGalleryImage"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        return super(). form_valid(form)


class CropImageError(Exception):
    pass




def get_cropped_file(request, instance, cropped_result,
                     image_field_name, user_field_name, preview_size):

    try:
        x = int(float(cropped_result['x']))
        y = int(float(cropped_result['y']))
        width = int(float(cropped_result['width']))
        height = int(float(cropped_result['height']))
        rotate = int(float(cropped_result['rotate']))
    except Exception:
        raise CropImageError(
            gettext('There are errors, please refresh the page '
                    'or try again later'))

    old_image = getattr(instance, image_field_name)

    try:
        new_image = Image.open(old_image.path)
    except IOError:
        raise CropImageError(
            gettext('There are errors，please re-upload the image'))

    image_format = new_image.format

    if rotate != 0:
        # or it will raise "AttributeError: 'NoneType' object has no attribute
        # 'mode' error in pillow 3.3.0
        new_image = new_image.rotate(-rotate, expand=True)

    box = (x, y, x+width, y+height)
    new_image = new_image.crop(box)

    if new_image.mode != "RGB":
        # For example, png images
        new_image = new_image.convert("RGB")

    new_image_io = BytesIO()
    new_image.save(new_image_io, format=image_format)

    # Notice: we don't change the user_field to request.user, or else
    # superuser cropping will take the ownership of the image, and
    # result in permission error for the actual owner to visit
    # the image.
    new_instance = instance
    new_instance.pk = None

    setattr(new_instance, user_field_name, request.user)

    new_instance_image_field = getattr(new_instance, image_field_name)
    new_instance_image_field.save(
        name=os.path.basename(getattr(instance, image_field_name).name),
        content=ContentFile(new_image_io.getvalue()),
        save=False
    )
    new_instance.save()
    return get_serialized_image(
        new_instance, image_field_name=image_field_name, preview_size=preview_size)


@require_POST
@login_required
def upload(request):
    file = request.FILES['files[]'] if request.FILES else None
    if request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':
        return HttpResponseBadRequest(
            gettext("Only XMLHttpRequest requests are allowed"))

    if not file or not is_image(file):
        return HttpResponseBadRequest(
            gettext("Only images are allowed to be uploaded"))

    preview_size = request.POST.get('preview_size', conf.DEFAULT_THUMBNAIL_SIZE)

    instance = BuiltInGalleryImage.objects.create(
        image=file,
        creator=request.user
    )

    return JsonResponse(
        {"files":
             [get_serialized_image(instance=instance,
                                   preview_size=preview_size)]},
        status=200)


@login_required
@require_GET
def fetch(request):

    if request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':
        return HttpResponseBadRequest(
            gettext("Only XMLHttpRequest requests are allowed"))

    pks = request.GET.get("pks", None)
    if not pks:
        return HttpResponseBadRequest()

    preview_size = request.GET.get('preview_size', conf.DEFAULT_THUMBNAIL_SIZE)

    pks = json.loads(unquote(pks))

    files = get_ordered_serialized_images(
        request, pks, image_model_class=BuiltInGalleryImage,
        image_field_name="image", user_field_name="creator",
        preview_size=preview_size
    )

    return JsonResponse(
        {"files": files}, status=200)


@login_required
@require_POST
def crop(request, *args, **kwargs):

    if request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':
        return HttpResponseBadRequest(
            gettext("Only XMLHttpRequest requests are allowed"))

    try:
        pk = request.POST["pk"]
        cropped_result = json.loads(request.POST.get("croppedResult"))
    except Exception as e:
        return JsonResponse(
            {
                'message':
                    (gettext('Bad Request:')
                     + '%s: %s' % (type(e).__name__, str(e)))},
            status=400)

    preview_size = request.POST.get('preview_size')

    image_model_class = BuiltInGalleryImage
    image_field_name = "image"
    user_field_name = "creator"

    instance = get_object_or_404(image_model_class, pk=pk)
    creator = getattr(instance, user_field_name)

    # Basic permission check
    if creator != request.user and not request.user.is_superuser:
        raise PermissionDenied(
            gettext("Only owner or superuser may crop the image"))

    try:
        file = get_cropped_file(
            request, instance, cropped_result, image_field_name,
            user_field_name, preview_size)
    except Exception as e:
        return JsonResponse({
            'message': "%(type_e)s: %(str_e)s" % {
                "type_e": type(e).__name__,
                "str_e": str(e)}},
            status=400)

    return JsonResponse(
        {
            "file": file,
            'message': gettext('Done!')
        },
        status=200)
