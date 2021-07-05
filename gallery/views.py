from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .backends import get_backend

from gallery.registry import get_image_model

from PIL import Image
from io import BytesIO


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
def upload(request, *args, **kwargs):

    file = request.FILES['files[]'] if request.FILES else None
    if not is_image(file):
        raise RuntimeError()

    backend = get_backend()

    file_wrapper = backend(file, request, *args, **kwargs)
    file_wrapper.save()

    file_dict = {
        'name': file_wrapper.get_image_file_name(),
        'size': file_wrapper.get_image_size(),

        'url': file_wrapper.get_image_url(),
        'thumbnailUrl': file_wrapper.get_thumbnail_url(),

        'deleteUrl': file_wrapper.get_delete_url(),
        'deleteType': 'POST',
    }
    return JsonResponse({"files": [file_dict]}, status=200)


@require_POST
def upload_delete(request, pk):
    image_model = get_image_model()
    try:
        instance = image_model.objects.get(pk=pk)
        # os.unlink(instance.file.path)
        instance.delete()
    except image_model.DoesNotExist:
        pass
    response = JsonResponse(False, safe=False)
    response['Content-Disposition'] = 'inline; filename=files.json'
    response['Content-Type'] = 'text/plain'
    return response
