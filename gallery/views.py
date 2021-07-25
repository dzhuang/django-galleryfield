from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.translation import gettext
from django.utils.text import format_lazy
from django.views.decorators.http import require_POST

try:  # pragma: no cover
    from django.apps import apps as django_apps
except ImportError:  # pragma: no cover
    from django.apps import django_apps

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
    model_str = request.POST['target_image_model']
    image_field_name = request.POST['image_field_name']
    creator_field_name = request.POST["creator_field_name"]

    model = django_apps.get_model(model_str)
    save_kwargs = {image_field_name: file,
                   creator_field_name: request.user}
    instance = model.objects.create(**save_kwargs)

    file_dict = {
        'pk': instance.pk,
        'name': instance.name,
        'size': instance.size,
        'url': instance.url,
        'thumbnailurl': instance.get_thumbnail_url(preview_size),

        'deleteurl': instance.delete_url,

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
    preview_size = request.POST['preview_size']
    model_str = request.POST['target_image_model']
    image_field_name = request.POST['image_field_name']
    creator_field_name = request.POST["creator_field_name"]

    image_model = django_apps.get_model(model_name=model_str)

    crop_instance = get_object_or_404(image_model(), pk=pk)

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

    image_orig_path = getattr(crop_instance, image_field_name).path

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

    save_kwargs = {image_field_name: new_image, creator_field_name: request.user}
    instance = image_model.objects.create(**save_kwargs)

    file_dict = {
        'pk': instance.pk,
        'name': instance.name,
        'size': instance.size,
        'url': instance.url,
        'thumbnailurl': instance.get_thumbnail_url(preview_size),

        'deleteurl': instance.delete_url,

        # todo: not implemented
        'cropurl': instance.crop_url,
    }

    return JsonResponse({"files": [file_dict], 'message': gettext('Done!')}, status=200)
