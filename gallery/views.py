import os
import json

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.utils.translation import gettext_lazy as _, gettext
from django.utils.text import format_lazy
from django.views.decorators.http import require_POST, require_GET

from .backends import get_backend

from gallery.registry import get_image_model

from PIL import Image
from io import BytesIO


def string_concat(*strings):
    return format_lazy("{}" * len(strings), *strings)


def is_image(file_obj):
    # verify closes the file
    try:
        Image.open(BytesIO(file_obj.read())).verify()
        return True
    except IOError:
        return False
    finally:
        file_obj.seek(0)


@require_POST
@login_required
def upload(request, *args, **kwargs):

    file = request.FILES['files[]'] if request.FILES else None
    if not is_image(file):
        raise RuntimeError()

    preview_size = request.POST['preview_size']
    model = request.POST['target_image_model']
    image_field_name = request.POST['image_field_name']

    from .backends import get_backend

    backend = get_backend()

    file_wrapper = backend(model, image_field_name, file, request, *args, **kwargs)
    file_wrapper.save()

    file_dict = {
        'pk': file_wrapper.pk,
        'name': file_wrapper.name,
        'size': file_wrapper.size,

        'url': file_wrapper.url,
        'thumbnailurl': file_wrapper.get_thumbnail_url(preview_size),

        'deleteurl': file_wrapper.delete_url,

        # todo: not implemented
        # 'cropurl': file_wrapper.crop_url,
    }
    return JsonResponse({"files": [file_dict]}, status=200)


class CropImageError(Exception):
    pass


# todo: not implemented yet
@login_required
@require_POST
def crop(request, *args, **kwargs):
    if not request.is_ajax():
        raise CropImageError(gettext('Only Ajax Post is allowed.'))

    pk = kwargs.get("pk")

    crop_instance = get_object_or_404(get_image_model(), pk=pk)

    import json
    json_data = json.loads(request.POST.get("croppedResult"))

    try:
        x = int(float(json_data['x']))
        y = int(float(json_data['y']))
        width = int(float(json_data['width']))
        height = int(float(json_data['height']))
        rotate = int(float(json_data['rotate']))
    except KeyError:
        raise CropImageError(
            gettext('There are errors, please refresh the page '
              'or try again later'))

    image_orig_path = crop_instance.image.path

    try:
        new_image = Image.open(image_orig_path)
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
        # for example, png images
        new_image = new_image.convert("RGB")

    new_image_io = BytesIO()
    new_image.save(new_image_io, format=image_format)

    backend = get_backend()
    file_wrapper = backend(new_image, request, *args, **kwargs)
    file_wrapper.save()

    file_dict = {
        'name': file_wrapper.get_image_file_name(),
        'size': file_wrapper.get_image_size(),

        'url': file_wrapper.get_image_url(),
        'thumbnailUrl': file_wrapper._get_thumbnail_url(),

        'deleteUrl': file_wrapper.get_delete_url(),
        'deleteType': 'POST',
        'crop_handler_url': file_wrapper.get_crop_url(),
        'pk': file_wrapper.pk,
    }

    return JsonResponse({"files": [file_dict], 'message': gettext('Done!')}, status=200)

# }}}
