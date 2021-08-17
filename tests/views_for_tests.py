from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.translation import gettext
from django.views.decorators.http import require_POST, require_GET

# {{{ The following 3 views are for testing whether upload, fetch, crop has
# customized views instead of built-in views


@require_POST
@login_required
def fake_upload(request):
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
def fake_crop(request):
    return JsonResponse(
        {
            "file": {},
            'message': gettext('Done!')
        },
        status=200)

# }}}
