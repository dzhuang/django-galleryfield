import os
import json
from urllib.parse import unquote
from sorl.thumbnail import get_thumbnail
from PIL import Image
from io import BytesIO

from django import forms
from django.views.generic import CreateView, UpdateView, View
from django.views.generic.list import BaseListView
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.apps import apps
from django.forms.models import modelform_factory
from django.utils.translation import gettext
from django.db.models import When, Case, QuerySet
from django.core.files.base import ContentFile
from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder

from gallery.utils import get_or_check_image_field
from gallery import conf


class BaseImageModelMixin:
    target_model = None
    crop_url_name = None

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

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.setup_model_and_image_field()
        self.preview_size = self.get_and_validate_preview_size_from_request()

    def dispatch(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':
            return HttpResponseBadRequest(
                gettext("Only XMLHttpRequest requests are allowed"))
        return super().dispatch(request, *args, **kwargs)

    def get_and_validate_preview_size_from_request(self):
        method = self.request.method.lower()
        if method == "get":
            request_dict = self.request.GET
        else:
            request_dict = self.request.POST

        # todo: validate and process situation like 60x80
        return request_dict.get('preview_size', conf.DEFAULT_THUMBNAIL_SIZE)

    def get_thumbnail(self, image):
        return get_thumbnail(
            image,
            "%sx%s" % (self.preview_size, self.preview_size),
            crop="center",
            quality=conf.DEFAULT_THUMBNAIL_QUALITY)

    def get_serialized_image(self, obj):
        image = getattr(obj, self._image_field_name)

        result = {
            'pk': obj.pk,
            'name': os.path.basename(image.path),
            'url': image.url,
        }

        try:
            image_size = image.size
        except OSError:
            result["error"] = gettext("The image was unexpectedly deleted from server")
        else:
            result.update({
                "size": image_size,
                "cropUrl": reverse(self.crop_url_name, kwargs={"pk": obj.pk})
            })

        try:
            # When the image file is deleted, it's thumbnail could still exist
            # because of cache.
            result['thumbnailUrl'] = self.get_thumbnail(image).url
        except Exception:
            pass

        return result

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.

        Pass response_kwargs to the constructor of the response class.
        """
        encoder = response_kwargs.pop("encoder", DjangoJSONEncoder)
        safe = response_kwargs.pop("safe", True)
        json_dumps_params = response_kwargs.pop("json_dumps_params", None)
        return JsonResponse(
            context, encoder, safe, json_dumps_params, **response_kwargs)


class ImageFormViewMixin:
    def get_form_class(self):
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

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, form):
        context = {}
        if self.object:
            context["files"] = [self.get_serialized_image(self.object)]
        if form.errors:
            context["errors"] = form.errors
        return context


class BaseCreateMixin(ImageFormViewMixin, BaseImageModelMixin):
    http_method_names = ['post']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

    def save_form_object(self, form):
        """This need to be implemented by subclasses
        for example::

          self.object = form.save(commit=False)
          self.object.creator = self.request.user
          self.object.save()
        """
        raise NotImplementedError

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(
            self.get_context_data(form=form), status=400)


class ImageCreateView(BaseCreateMixin, CreateView):
    pass



class BaseListViewMixin(BaseImageModelMixin, BaseListView):
    # List view doesn't include a form
    target_model = "gallery.BuiltInGalleryImage"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self._pks = self.get_and_validate_pks_from_request()

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
        return pks

    def get_queryset(self):
        # We have to override this method, because currently super().get_queryset
        # doesn't accept Case in 'order_by'
        # See https://github.com/django/django/pull/14757
        queryset = self.model._default_manager.all()
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, (str, Case)):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset
        return queryset.filter(pk__in=self._pks)

    def get_ordering(self):
        preserved = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(self._pks)])
        return preserved

    def get_context_data(self, **kwargs):
        context = {
            "files":  [self.get_serialized_image(obj)
                       for obj in self.get_queryset()]}
        context.update(kwargs)

        return context


class ImageListView(BaseListViewMixin, BaseListView):
    def get_queryset(self):
        """
        You need to override this method to do some basic
        filter in terms of who can see which images.
        :return: A Queryset
        """
        return super().get_queryset()


class CropError(Exception):
    pass


class BaseCropViewMixin(ImageFormViewMixin, BaseImageModelMixin, UpdateView):
    http_method_names = ['post']

    # def get_form_class(self):
    #     this = self
    #
    #     class ImageForm(forms.ModelForm):
    #         cropped_result = forms.JSONField(required=True)
    #
    #         class Meta:
    #             model = this.model
    #             fields = (this._image_field_name,)
    #
    #         def clean_cropped_result(self):
    #             data = self.cleaned_data["cropped_result"]
    #
    #             for key in ["x", "y", "width", "height", "rotate"]:
    #                 try:
    #                     if not str(data[key]).isdigit():
    #                         raise forms.ValidationError(
    #                             gettext(
    #                                 'Invalid cropped_result %s'
    #                                 ' is expecting an int, while got %s'
    #                                 % (key, str(data[key]))))
    #                 except KeyError:
    #                     raise forms.ValidationError(
    #                         gettext('Invalid cropped_result: %s is missing' % key))
    #
    #     return ImageForm
    def get_form_class(self):
        this = self

        class ImageForm(forms.ModelForm):
            class Meta:
                model = this.model
                fields = (this._image_field_name,)

        return ImageForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self._cropped_result = self.get_and_validate_cropped_result_from_request()

    def get_and_validate_cropped_result_from_request(self):
        try:
            cropped_result = json.loads(self.request.POST.get("cropped_result"))
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
            except Exception as e:
                raise SuspiciousOperation(
                    gettext('There are errors, please refresh the page '
                            'or try again later'))

        return x, y, width, height, rotate, scale_x, scale_y

    # def post(self, request, *args, **kwargs):
    #     pass
    #
    # def get_form_kwargs(self):
    #     pass

    def get_cropped_uploaded_file(self):
        old_image = getattr(self.current_instance, self._image_field_name)

        print("first we had %s " % str(self.object.pk))

        try:
            new_image = Image.open(old_image.path)
        except IOError:
            raise CropError(
                gettext('There are errors，please re-upload the image'))

        image_format = new_image.format

        x, y, width, height, rotate, scale_x, scale_y = self._cropped_result

        if rotate != 0:
            # or it will raise "AttributeError: 'NoneType' object has no attribute
            # 'mode' error in pillow 3.3.0
            new_image = new_image.rotate(-rotate, expand=True)

        box = (x, y, x + width, y + height)
        new_image = new_image.crop(box)

        # if new_image.mode != "RGB":
        #     # For example, png images
        #     new_image = new_image.convert("RGB")

        new_image_io = BytesIO()
        new_image.save(new_image_io, format=image_format)
        # size = new_image_io.tell()
        # print(size)

        # Image.MIME[image_format]

        upload_file = InMemoryUploadedFile(
            file=new_image_io,
            field_name=self._image_field_name,
            name=old_image.name,
            content_type=Image.MIME[image_format],
            size=new_image_io.tell(),
            charset=None
        )
        return upload_file

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.current_instance = kwargs.pop("instance")
        kwargs.update({
            "files": {self._image_field_name: self.get_cropped_uploaded_file()},
        })
        return kwargs

    def get_cropped_instance(self, current_instance):
        old_image = getattr(current_instance, self._image_field_name)

        print("first we had %s " % str(self.object.pk))

        try:
            new_image = Image.open(old_image.path)
        except IOError:
            raise CropError(
                gettext('There are errors，please re-upload the image'))

        image_format = new_image.format

        x, y, width, height, rotate, scale_x, scale_y = self._cropped_result

        if rotate != 0:
            # or it will raise "AttributeError: 'NoneType' object has no attribute
            # 'mode' error in pillow 3.3.0
            new_image = new_image.rotate(-rotate, expand=True)

        box = (x, y, x + width, y + height)
        new_image = new_image.crop(box)

        # if new_image.mode != "RGB":
        #     # For example, png images
        #     new_image = new_image.convert("RGB")

        new_image_io = BytesIO()
        new_image.save(new_image_io, format=image_format)

        image_field_name = self._image_field_name

        # We did not actually update the original instance,
        # instead, we created another instance.
        new_obj = self.object
        new_obj.pk = None

        new_instance_image_field = getattr(new_obj, image_field_name)
        new_instance_image_field.save(
            name=os.path.basename(getattr(current_instance, image_field_name).name),
            content=ContentFile(new_image_io.getvalue()),
            save=False
        )
        new_obj.save()
        print("now we had %s " % str(new_obj.pk))
        return new_obj

    # def get_form_kwargs(self):
    #     form_kwargs = super().get_form_kwargs()
    #     form_kwargs.pop("instance")
    #
    #     kwargs.update({
    #         'data': self.request.POST,
    #         'files': {
    #             self._image_field_name: self.get_and_validate_file_from_request()},
    #     })
    #     return kwargs

    def get_context_data(self, **kwargs):
        context = {
            "files":  [self.get_serialized_image(obj)
                       for obj in self.get_queryset()]}
        context.update(kwargs)
        return context

    def form_valid(self, form):
        print("form is valid")
        print(form.instance)
        # super().form_valid(form)
        print("Now we had %s " % str(self.object.pk))
        # print(self.object.pk)
        newobject = form.save(commit=False)
        self.object = self.current_instance
        self.object.pk = None

        setattr(self.object, self._image_field_name, getattr(newobject, self._image_field_name))
        self.object.save()
        return super().form_valid(form)
        # try:
        #     self.object = self.get_cropped_instance(self.object)
        # except Exception as e:
        #     return JsonResponse({
        #         'message': "%(type_e)s: %(str_e)s" % {
        #             "type_e": type(e).__name__,
        #             "str_e": str(e)}},
        #         status=400)

        return JsonResponse(
            {
                "file": self.get_serialized_image(self.object),
                'message': gettext('Done!')
            },
            status=200)


class ImageCropView(BaseCropViewMixin, UpdateView):
    def get_context_data(self, **kwargs):
        print("here!!!")
        return super().get_context_data(**kwargs)

    def form_invalid(self, form):
        return super().form_valid(form)

