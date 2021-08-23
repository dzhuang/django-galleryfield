import json
import os
from io import BytesIO
from urllib.parse import unquote

from django import forms
from django.apps import apps
from django.core.exceptions import (ImproperlyConfigured, PermissionDenied,
                                    SuspiciousOperation)
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Case, When
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext
from django.views.generic import UpdateView
from django.views.generic.list import BaseListView
from PIL import Image
from sorl.thumbnail import get_thumbnail

from galleryfield import conf, defaults
from galleryfield.utils import (get_formatted_thumbnail_size,
                                get_or_check_image_field)


class BaseImageModelMixin:
    """
    :attr:`target_model`: A valid target image model used by the view.
    :attr:`crop_url_name`: str, An URL name or an URL for handling server side
       cropping of uploaded images, if configured None, it will used the value
       in the form of ``app_label-model_name-crop`` in lower case. For example, if
       ``self.target_model`` is ``my_app.MyImage``, then the `crop_url_name`
       is auto-configured to ``my_app-myimage-crop``. You need to make sure you
       had that URL name in your URL_CONF and related views exists.

    :attr:`disable_server_side_crop`: bool, determining whether server side crop
       for this view will be enabled, defaults to True. If False, related widget
       ui won't show `Edit` buttons for uploaded images.
    """
    target_model = None
    crop_url_name = None
    disable_server_side_crop = True

    def setup(self, request, *args, **kwargs):
        # XML request only check
        if request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':
            raise PermissionDenied(
                gettext("Only XMLHttpRequest requests are allowed"))

        super().setup(request, *args, **kwargs)
        self.setup_model_and_image_field()
        self.validate_crop_url()
        self.thumbnail_size = self.get_and_validate_thumbnail_size_from_request()

    def setup_model_and_image_field(self):
        if self.target_model is None:
            raise ImproperlyConfigured(
                "Using BaseImageModelMixin (base class of %s) without "
                "the 'target_model' attribute is prohibited."
                % self.__class__.__name__
            )

        self._image_field_name = (get_or_check_image_field(
            obj=self, target_model=self.target_model,
            check_id_prefix=self.__class__.__name__,
            is_checking=False).name)
        self.model = apps.get_model(self.target_model)

    def validate_crop_url(self):
        if self.disable_server_side_crop:
            return
        if self.crop_url_name is None:
            app_model_name = "-".join(self.target_model.split(".")).lower()
            self.crop_url_name = "%s-crop" % app_model_name
        try:
            reverse(self.crop_url_name, kwargs={"pk": 1})
        except Exception as e:
            raise ImproperlyConfigured(
                "'crop_url_name' in %s is invalid. The exception is: "
                "%s: %s."
                % (self.__class__.__name__,
                   type(e).__name__,
                   str(e)))
        if (self.crop_url_name == defaults.DEFAULT_CROP_URL_NAME
                and self.target_model != defaults.DEFAULT_TARGET_IMAGE_MODEL):
            raise ImproperlyConfigured(
                    "'crop_url_name' in %s is using built-in default, while "
                    "'target_model' is not using built-in default value. They "
                    "are handling different image models. This is prohibited."
                    % self.__class__.__name__
            )

    def get_and_validate_thumbnail_size_from_request(self):
        # Get preview size from request
        method = self.request.method.lower()

        if method == "get":
            # If thumbnail_size is a list, request query string should be in
            # the form of &thumbnail_size=100&thumbnail_size=150, and the
            # 'get' method should be 'getlist'
            # Ref: https://stackoverflow.com/a/30107874/3437454
            thumbnail_size = self.request.GET.getlist(
                'thumbnail_size', conf.DEFAULT_THUMBNAIL_SIZE)
            error_msg = gettext(
                "'thumbnail_size' must be an int, or a string of int, "
                "or a string in the form of '80x60', or a list of"
                "2 ints, e.g, [80, 60]. "
                "Ref: https://stackoverflow.com/a/30107874/3437454"
            )
        else:
            thumbnail_size = self.request.POST.get(
                'thumbnail_size', conf.DEFAULT_THUMBNAIL_SIZE)
            error_msg = gettext(
                "'thumbnail_size' must be an int, or a string of int, "
                "or a string in the form of '80x60', or a list or tuple of "
                "2 ints, e.g, [80, 60] or (80, 60)."
            )

        try:
            return get_formatted_thumbnail_size(thumbnail_size)
        except Exception:
            raise ImproperlyConfigured(error_msg)

    def get_thumbnail(self, image):
        return get_thumbnail(
            file_=image,
            geometry_string=self.thumbnail_size,
            crop="center",
            quality=conf.DEFAULT_THUMBNAIL_QUALITY)

    def get_serialized_image(self, obj):
        # This is used to construct return value file dict in
        # upload list and crop views.
        image = getattr(obj, self._image_field_name)

        result = {
            'pk': obj.pk,
            'name': os.path.basename(image.path),
            'url': image.url,
        }

        error = []

        try:
            image_size = image.size
        except OSError:
            error.append(gettext(
                "image: The image was unexpectedly deleted from server"))
        else:
            result.update({
                "size": image_size,
            })

        if not self.disable_server_side_crop:
            result["cropUrl"] = reverse(self.crop_url_name, kwargs={"pk": obj.pk})

        try:
            result['thumbnailUrl'] = self.get_thumbnail(image).url
        except Exception as e:
            error.append(
                gettext("thumbnail: %s: %s" % (type(e).__name__, str(e)))
            )

        if error:
            result["error"] = "; ".join(error)
        return result

    def render_to_response(self, context, **response_kwargs):
        # Overriding the method from template view, we don't need
        # a template in rendering the JsonResponse
        encoder = response_kwargs.pop("encoder", DjangoJSONEncoder)
        safe = response_kwargs.pop("safe", True)
        json_dumps_params = response_kwargs.pop("json_dumps_params", None)
        return JsonResponse(
            context, encoder, safe, json_dumps_params, **response_kwargs)


class ImageFormViewMixin:
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.form_class = self.get_form_class()

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, form):
        context = {}
        if form.is_valid():
            if self.object:
                context["files"] = [self.get_serialized_image(self.object)]
                context["message"] = gettext("Done")
        else:
            context["errors"] = form.errors

        return context


class BaseCreateMixin(ImageFormViewMixin, BaseImageModelMixin):
    http_method_names = ['post']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

    def get_form_class(self):
        # Here we were simulating the request is done through
        # a form. In this way, we can used ImageField to validate
        # the file.

        this = self

        class ImageForm(forms.ModelForm):
            class Meta:
                model = this.model
                fields = (this._image_field_name,)

            def __init__(self, files=None, **kwargs):
                if files is not None:
                    # When getting data from ajax post
                    files = {this._image_field_name: files["files[]"]}
                return super().__init__(files=files, **kwargs)

        return ImageForm

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form error."""
        return self.render_to_response(
            self.get_context_data(form=form), status=400)


class BaseListViewMixin(BaseImageModelMixin, BaseListView):
    # List view doesn't include a form

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self._pks = self.get_and_validate_pks_from_request()

    def get_and_validate_pks_from_request(self):
        # convert the request data "pks" (which is supposed to
        # be a stringfied json string) into a list of
        # image instance "pk".
        pks = self.request.GET.get("pks", None)
        if not pks:
            raise SuspiciousOperation(
                gettext("The request doesn't contain pks data"))

        try:
            pks = json.loads(unquote(pks))
            assert isinstance(pks, list)
        except Exception as e:
            raise SuspiciousOperation(
                gettext("Invalid format of pks %s: %s: %s" %
                        (str(pks), type(e).__name__, str(e))))
        else:
            for pk in pks:
                if not str(pk).isdigit():
                    raise SuspiciousOperation(
                        gettext(
                            "pks should only contain integers, while got %s"
                            % str(pk)))
        return pks

    def get_queryset(self):
        # We have to override this method, because currently super().get_queryset
        # doesn't accept Case in 'order_by'
        # See https://github.com/django/django/pull/14757
        queryset = self.model._default_manager.all()
        ordering = self.get_ordering()
        if ordering:  # pragma: no cover
            if not isinstance(ordering, (list, tuple)):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset.filter(pk__in=self._pks)

    def get_ordering(self):
        # Preserving the sequence while filter by (id__in=pks)
        # See https://stackoverflow.com/a/37648265/3437454
        preserved = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(self._pks)])
        return preserved

    def get_context_data(self, **kwargs):
        # Return a list of serialized files
        context = {
            "files":  [self.get_serialized_image(obj)
                       for obj in self.get_queryset()]}
        context.update(kwargs)

        return context


class CropError(Exception):
    pass


class BaseCropViewMixin(ImageFormViewMixin, BaseImageModelMixin, UpdateView):
    http_method_names = ['post']

    def get_form_class(self):
        # Here we were simulating the request is done through
        # a form. In this way, we can used ImageField to validate
        # the file.
        this = self

        class ImageForm(forms.ModelForm):
            class Meta:
                model = this.model
                fields = (this._image_field_name,)

            def __init__(self, **kwargs):
                super().__init__(**kwargs)

                new_uploaded_file = this.get_cropped_uploaded_file(self.instance)
                self.instance.pk = None
                self.initial = {this._image_field_name: new_uploaded_file}

        return ImageForm

    def setup(self, request, *args, **kwargs):
        if self.disable_server_side_crop:
            raise SuspiciousOperation(
                gettext("Server side crop is not enabled."))
        super().setup(request, *args, **kwargs)
        self._cropped_result = self.get_and_validate_cropped_result_from_request()

    def get_and_validate_cropped_result_from_request(self):
        try:
            cropped_result = json.loads(self.request.POST["cropped_result"])
        except Exception as e:
            if isinstance(e, KeyError):
                raise SuspiciousOperation(
                    gettext("The request doesn't contain cropped_result"))
            raise SuspiciousOperation(
                gettext("Error while getting cropped_result: %s: %s"
                        % (type(e).__name__, str(e))))
        else:
            try:
                x = int(float(cropped_result['x']))
                y = int(float(cropped_result['y']))
                width = int(float(cropped_result['width']))
                height = int(float(cropped_result['height']))
                rotate = int(float(cropped_result['rotate']))

                # todo: allow show resized image in model ui
                try:
                    scale_x = float(cropped_result['scaleX'])
                except KeyError:
                    scale_x = None
                try:
                    scale_y = float(cropped_result['scaleY'])
                except KeyError:
                    scale_y = None
            except Exception:
                raise SuspiciousOperation(
                    gettext('Wrong format of crop_result data.'))

        return x, y, width, height, rotate, scale_x, scale_y

    def get_cropped_uploaded_file(self, old_instance):
        # This view is put into the init method of self.form_class (i.e., ImageForm)
        # to simulate we posted a NEW image in the form to create a (cropped) NEW
        # image
        old_image = getattr(old_instance, self._image_field_name)

        try:
            new_image = Image.open(old_image.path)
        except IOError:
            raise SuspiciousOperation(
                gettext('File not found，please re-upload the image'))

        image_format = new_image.format

        x, y, width, height, rotate, scale_x, scale_y = self._cropped_result

        if rotate != 0:
            # or it will raise "AttributeError: 'NoneType' object has no attribute
            # 'mode' error in pillow 3.3.0
            new_image = new_image.rotate(-rotate, expand=True)

        box = (x, y, x + width, y + height)
        new_image = new_image.crop(box)

        new_image_io = BytesIO()
        new_image.save(new_image_io, format=image_format)

        upload_file = InMemoryUploadedFile(
            file=new_image_io,
            field_name=self._image_field_name,
            name=old_image.name,
            content_type=Image.MIME[image_format],
            size=new_image_io.tell(),
            charset=None
        )
        return upload_file
