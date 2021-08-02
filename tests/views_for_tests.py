from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.translation import gettext
from django.views.decorators.http import require_POST, require_GET


@require_POST
@login_required
def fake_upload(request, *args, **kwargs):

    return JsonResponse(
        {"files": []},
        status=200)


@login_required
@require_GET
def fake_fetch(request):
    return JsonResponse(
        {"files": []}, status=200)


@login_required
@require_POST
def fake_crop(request, *args, **kwargs):
    return JsonResponse(
        {
            "file": {},
            'message': gettext('Done!')
        },
        status=200)
