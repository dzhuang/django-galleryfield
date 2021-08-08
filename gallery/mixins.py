from django import forms
from django.views.generic import CreateView, UpdateView, ListView
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.apps import apps
from django.forms.models import modelform_factory
from django.utils.translation import gettext

from gallery.utils import get_or_check_image_field, is_image, get_serialized_image
from gallery import conf


class RequireXMLRequestMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':
            return HttpResponseBadRequest(
                gettext("Only XMLHttpRequest requests are allowed"))
        return super().dispatch(request, *args, **kwargs)


class BaseCreateMixin:
    http_method_names = ['post']

    def form_valid(self, form):
        return JsonResponse({"files":
             [get_serialized_image(instance=self.object,
                                   preview_size=self._preview_size)]})


class ImageCreateMixin(RequireXMLRequestMixin, BaseCreateMixin):
    target_model = None

    def get_form_class(self):
        if self.target_model is None:
            raise ImproperlyConfigured(
                "Using ImageCreateMixin (base class of %s) without "
                "the 'fields' attribute is prohibited." % self.__class__.__name__
            )
        self.image_field_name = (get_or_check_image_field(
            obj=self, target_model=self.target_model,
            check_id_prefix=self.__class__.__name__,
            is_checking=False).name)
        model = apps.get_model(self.target_model)
        image_field = self.image_field_name
        return modelform_factory(model, fields=[image_field])

    def get_form_kwargs(self):
        kwargs = {
            'prefix': self.get_prefix(),
        }

        file = self.request.FILES['files[]'] if self.request.FILES else None

        if not file or not is_image(file):
            raise SuspiciousOperation(
                gettext("Only images are allowed to be uploaded"))

        self._preview_size = self.request.POST.get(
            'preview_size', conf.DEFAULT_THUMBNAIL_SIZE)

        kwargs.update({
            'data': self.request.POST,
            'files': {self.image_field_name: file},
        })
        return kwargs

    def form_valid(self, form):
        """This method should be overridden if model instance require
        more field other than the image field
        """
        self.object = form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""

        return HttpResponseBadRequest(form.errors)
