import os
import json
from urllib.parse import unquote
from sorl.thumbnail import get_thumbnail
from PIL import Image
from io import BytesIO

from django.views.generic import CreateView, UpdateView
from django.views.generic.list import BaseListView
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.apps import apps
from django.forms.models import modelform_factory
from django.utils.translation import gettext
from django.db.models import When, Value, Case, IntegerField
from django.core.files.base import ContentFile
from django.urls import reverse

from gallery.utils import get_or_check_image_field
from gallery import conf


class RequireXMLRequestMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':
            return HttpResponseBadRequest(
                gettext("Only XMLHttpRequest requests are allowed"))
        return super().dispatch(request, *args, **kwargs)


class BaseImageModelMixin:
    target_model = None
    crop_url_name = None

    @staticmethod
    def is_image(file_obj):
        # Verify and close the file
        try:
            Image.open(BytesIO(file_obj.read())).verify()
            return True
        except IOError:
            return False
        finally:
            file_obj.seek(0)

    def setup_model_and_image_field(self):
        if self.target_model is None:
            raise ImproperlyConfigured(
                "Using BaseImageModelMixin (base class of %s) without "
                "the 'target_model' attribute is prohibited."
                % self.__class__.__name__
            )
        if self.crop_url_name is None:
            raise ImproperlyConfigured(
                "Using BaseImageModelMixin (base class of %s) without "
                "the 'crop_url_name' attribute is prohibited."
                % self.__class__.__name__
            )
        else:
            try:
                reverse(self.crop_url_name, kwargs={"pk": 1})
            except Exception as e:
                raise ImproperlyConfigured(
                    "'crop_url_name' in %s is invalid. The exception is: "
                    "%s: %s."
                    % (self.__class__.__name__,
                       type(e).__name__,
                       str(e)))

        self._image_field_name = (get_or_check_image_field(
            obj=self, target_model=self.target_model,
            check_id_prefix=self.__class__.__name__,
            is_checking=False).name)
        self.model = apps.get_model(self.target_model)

    def get_form_class(self):
        self.setup_model_and_image_field()
        return modelform_factory(
            self.model, fields=[self._image_field_name])

    def get_and_validate_preview_size_from_request(self):
        method = self.request.method.lower()
        if method == "get":
            request_dict = self.request.GET
        else:
            request_dict = self.request.POST

        # todo: validate and process situation like 60x80
        return request_dict.get('preview_size', conf.DEFAULT_THUMBNAIL_SIZE)

    def get_thumbnail(self, image):
        preview_size = self.get_and_validate_preview_size_from_request()
        return get_thumbnail(
            image,
            "%sx%s" % (preview_size, preview_size),
            crop="center",
            quality=conf.DEFAULT_THUMBNAIL_QUALITY)

    def get_serialized_image(self, obj):
        image = getattr(obj, self._image_field_name)

        return {
            'pk': obj.pk,
            'name': os.path.basename(image.path),
            'size': image.size,
            'url': image.url,
            'thumbnailUrl': self.get_thumbnail(image).url,
            'cropUrl': reverse(self.crop_url_name, kwargs={"pk": obj.pk})
        }


class BaseCreateMixin(RequireXMLRequestMixin, BaseImageModelMixin):
    http_method_names = ['post']

    def get_and_validate_file_from_request(self):
        file = self.request.FILES['files[]'] if self.request.FILES else None

        if not file or not self.is_image(file):
            raise SuspiciousOperation(
                gettext("Only images are allowed to be uploaded"))
        return file

    def get_form_kwargs(self):
        kwargs = {
            'prefix': self.get_prefix(),
        }

        kwargs.update({
            'data': self.request.POST,
            'files': {
                self._image_field_name: self.get_and_validate_file_from_request()},
        })
        return kwargs

    def save_form_object(self, form):
        """This need to be implemented by subclasses
        for example::

          self.object = form.save(commit=False)
          self.object.creator = self.request.user
          self.object.save()
        """
        raise NotImplementedError

    def form_valid(self, form):
        self.save_form_object(form)
        return JsonResponse({"files":
             [self.get_serialized_image(self.object)]})

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        return HttpResponseBadRequest(form.errors)


class ImageCreateView(BaseCreateMixin, CreateView):
    pass


class BaseListViewMixin(RequireXMLRequestMixin, BaseImageModelMixin):
    target_model = "gallery.BuiltInGalleryImage"

    def get_and_validate_pks_from_request(self):
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
        self.pks = pks
        return pks

    def get_queryset(self):
        """This method should be overridden if you want to added more
        constraints as to who can view the images (request.user only)
        or other conditions (creation time)
        """
        return super().get_queryset()

    def get_ordered_queryset(self):
        """
        Preserving the order of image using id__in=pks
        # https://stackoverflow.com/a/37146498/3437454
        We had to do this after get_query because
        chaining extra filter on annotation can get messy
        """
        pks = self.get_and_validate_pks_from_request()
        queryset = self.get_queryset()
        queryset = queryset.filter(id__in=self.pks)

        cases = [When(id=x, then=Value(i)) for i, x in enumerate(pks)]
        case = Case(*cases, output_field=IntegerField())

        queryset = queryset.annotate(pk_order=case).order_by('pk_order')
        return queryset

    def get(self, request, *args, **kwargs):
        self.setup_model_and_image_field()
        files = [self.get_serialized_image(obj)
                 for obj in self.get_ordered_queryset()]
        return JsonResponse(
            {"files": files}, status=200)


class ImageListView(BaseListViewMixin, BaseListView):
    pass


class CropError(Exception):
    pass


class BaseCropViewMixin(RequireXMLRequestMixin, BaseImageModelMixin):
    http_method_names = ['post']

    def get_queryset(self):
        self.setup_model_and_image_field()
        return super().get_queryset()

    def get_and_validate_cropped_result_from_request(self):
        try:
            cropped_result = json.loads(self.request.POST.get("croppedResult"))
        except Exception as e:
            if isinstance(e, KeyError):
                raise SuspiciousOperation(
                    gettext("The request doesn't contain croppedResult"))
            raise SuspiciousOperation(
                gettext("Error while getting croppedResult: %s: %s"
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
                raise CropError(
                    gettext('There are errors, please refresh the page '
                            'or try again later'))

        return x, y, width, height, rotate, scale_x, scale_y

    def get_cropped_instance(self):
        old_image = getattr(self.object, self._image_field_name)

        try:
            new_image = Image.open(old_image.path)
        except IOError:
            raise CropError(
                gettext('There are errors，please re-upload the image'))

        image_format = new_image.format

        x, y, width, height, rotate, scale_x, scale_y = (
            self.get_and_validate_cropped_result_from_request())

        if rotate != 0:
            # or it will raise "AttributeError: 'NoneType' object has no attribute
            # 'mode' error in pillow 3.3.0
            new_image = new_image.rotate(-rotate, expand=True)

        box = (x, y, x + width, y + height)
        new_image = new_image.crop(box)

        if new_image.mode != "RGB":
            # For example, png images
            new_image = new_image.convert("RGB")

        new_image_io = BytesIO()
        new_image.save(new_image_io, format=image_format)

        image_field_name = self._image_field_name

        # We did not actually update the original instance,
        # instead, we created another instance.
        new_obj = self.object
        new_obj.pk = None

        new_instance_image_field = getattr(new_obj, image_field_name)
        new_instance_image_field.save(
            name=os.path.basename(getattr(self.object, image_field_name).name),
            content=ContentFile(new_image_io.getvalue()),
            save=False
        )
        new_obj.save()
        return new_obj

    def form_valid(self, form):
        try:
            self.object = self.get_cropped_instance()
        except Exception as e:
            return JsonResponse({
                'message': "%(type_e)s: %(str_e)s" % {
                    "type_e": type(e).__name__,
                    "str_e": str(e)}},
                status=400)

        return JsonResponse(
            {
                "file": self.get_serialized_image(self.object),
                'message': gettext('Done!')
            },
            status=200)


class ImageCropView(BaseCropViewMixin, UpdateView):
    pass
