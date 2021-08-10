import json
import re

from django import forms
from django.core.exceptions import ImproperlyConfigured

from gallery_widget import conf, defaults
from gallery_widget.utils import (
    get_url_from_str, convert_dict_to_plain_text, get_formatted_thumbnail_size)

NoReverseMatch_EXCEPTION_STR_RE = re.compile("Reverse for '(.+)' not found")


class GalleryWidget(forms.HiddenInput):
    """This is the default widget used by :class:`gallery_widget.fields.GalleryFormField`.

    :param upload_handler_url: An URL name or an url of the upload handler
           view used by the widget instance, defaults to `None`. If `None`, 
           upload ui won't show upload buttons. When the parent 
           :class:`gallery_widget.fields.GalleryFormField` is used by
           a :class:`gallery_widget.fields.GalleryField`, that url will be auto-configured,
           with the value in the form of ``modelname-upload`` in lower case.
           For example, if ``target_model`` is ``myapp.MyImageModel``, then
           the `upload_handler_url` is auto-configured to ``myimagemodel-upload``.
           You need to make sure you had that URL name in your URL_CONF and 
           related views exists.
    :type upload_handler_url: str, optional
    :param fetch_request_url: An URL name or an url for fetching the existing
           images in the gallery_widget instance, defaults to `None`. If `None`, 
           upload ui won't load existing images. Like ``upload_handler_url``,
           this param will be auto-configured in the form of ``modelname-fetch``.
    :type fetch_request_url: str, optional
    :param multiple: Whether allow to select multiple image files in the 
           file picker.
    :type multiple: bool, optional
    :param thumbnail_size: The thumbnail size (both width and height), defaults 
           to ``defaults.DEFAULT_THUMBNAIL_SIZE``, which can be overridden by
           ``settings.DJANGO_GALLERY_WIDGET_CONFIG["thumbnails"]["size"]``.
           The value can be set after the widget is initialized.
    :type thumbnail_size: int, optional
    :param template: The path of template which is used to render the widget.
           defaults to ``gallery_widget/widget.html``, which support template 
           inheritance.
    :type template: str, optional     
    :param attrs: Html attribute when rendering the field (Which is a 
           :class:`django.forms.HiddenInput`), defaults to `None`. See 
           `Django docs <https://docs.djangoproject.com/en/dev/ref/forms/widgets/#django.forms.Widget.attrs>`_.
    :type attrs: dict, optional
    :param options: Other options when rendering the widget. Implemented options:

           * **accepted_mime_types** (`list`, `optional`) - A list of MIME types
             used to filter files when picking files with file picker, defaults to ``['image/*']``
    :type options: dict, optional
    :param jquery_upload_ui_options: The default template is using 
           blueimp/jQuery-File-Upload package to render the ui and dealing with
           AJAX upload. This param can be used to set the options. See
           `jQuery-File-Upload Wiki <https://github.com/blueimp/jQuery-File-Upload/wiki/Options#singlefileuploads>`_
           for all the available options. The default options can be 
           seen in ``defaults.GALLERY_WIDGET_UI_DEFAULT_OPTIONS``. Notice that
           ``maxNumberOfFiles`` is overridden by the ``max_number_of_images`` param
           when initializing :class:`gallery_widget.fields.GalleryFormField`, and
           ``previewMaxWidth`` and ``previewMaxHeight`` are overridden by
           param ``thumbnail_size``.
    :type jquery_upload_ui_options: dict, optional
    :param disable_fetch: Whether disable fetching existing images of the
           form instance (if any), defaults to `False`. If True, the validity of
           ``fetch_request_url`` will not be checked.
    :type disable_fetch: bool, optional
    :param disable_server_side_crop: Whether disable server side cropping of 
           uploaded images, defaults to `False`. If True, the validity of
           ``crop_request_url`` will not be checked.
    :type disable_server_side_crop: bool, optional
    
    """  # noqa

    def __init__(
            self,
            upload_handler_url=None,
            fetch_request_url=None,
            multiple=True,
            thumbnail_size=conf.DEFAULT_THUMBNAIL_SIZE,
            template="gallery_widget/widget.html",
            attrs=None, options=None,
            jquery_upload_ui_options=None,
            disable_fetch=False,
            disable_server_side_crop=False,
            **kwargs):

        super(GalleryWidget, self).__init__(attrs)

        self.multiple = multiple
        self._thumbnail_size = get_formatted_thumbnail_size(thumbnail_size)
        self.template = template

        self.disable_fetch = disable_fetch
        self.disable_server_side_crop = disable_server_side_crop

        self._upload_handler_url = upload_handler_url

        self._fetch_request_url = (
            None if disable_fetch else fetch_request_url)

        jquery_upload_ui_options = jquery_upload_ui_options or {}
        _jquery_upload_ui_options = defaults.GALLERY_WIDGET_UI_DEFAULT_OPTIONS.copy()
        _jquery_upload_ui_options.update(jquery_upload_ui_options)

        # https://github.com/blueimp/jQuery-File-Upload/wiki/Options#singlefileuploads
        _jquery_upload_ui_options.pop("singleFileUploads", None)

        self.ui_options = _jquery_upload_ui_options
        self.options = options and options.copy() or {}
        self.options.setdefault("accepted_mime_types", ['image/*'])

    @property
    def thumbnail_size(self):
        return self._thumbnail_size

    @thumbnail_size.setter
    def thumbnail_size(self, value):
        self._thumbnail_size = get_formatted_thumbnail_size(value)

    @property
    def upload_handler_url(self):
        return self._upload_handler_url

    @upload_handler_url.setter
    def upload_handler_url(self, url):
        self._upload_handler_url = get_url_from_str(url)

    @property
    def fetch_request_url(self):
        return self._fetch_request_url

    @fetch_request_url.setter
    def fetch_request_url(self, url):
        self._fetch_request_url = (
            None if self.disable_fetch else get_url_from_str(url))

    def set_and_check_urls(self):
        # We now then the url names into an actual url, that
        # can't be down in __init__ because url_conf is not
        # loaded when doing the system check, and will result
        # in failure to start.
        try:
            self.upload_handler_url = get_url_from_str(
                    self.upload_handler_url, require_urlconf_ready=True)
        except Exception:
            raise ImproperlyConfigured(
                "'upload_handler_url' is invalid: %s is neither "
                "a valid url nor a valid url name."
                % self.upload_handler_url)

        try:
            self.fetch_request_url = get_url_from_str(
                    self.fetch_request_url, require_urlconf_ready=True)

        except Exception:
            raise ImproperlyConfigured(
                "'fetch_request_url' is invalid: %s is neither "
                "a valid url nor a valid url name."
                % self.fetch_request_url)

        # In the following we validate update the urls from url names (if it is
        # not an url) and check the potential conflicts of init params
        # of the widget with the target_image_model set to the widget.
        # For validation of urls, because those urls are assigned by reverse_lazy,
        # the result of which will only be validated until evaluation, we
        # can only do that until the request context is available.
        # For checking conflicts, the logic is: if the target_image_model is not
        # using the built-in model, i.e., defaults.DEFAULT_TARGET_IMAGE_MODEL,
        # then the upload, crop and fetch views should not use the built-in ones.
        # Because those views are using defaults.DEFAULT_TARGET_IMAGE_MODEL
        # as the target image model.
        # BTW, this check can't be done at the model/field check stage or formfield
        # init stage, because we should allow the widget be changed after the form
        # is initialized. So, we have to do this before rendering the widget,
        # and throw the error if any.

        target_image_model = getattr(self, "image_model", None)

        image_model_is_default = (
                target_image_model == defaults.DEFAULT_TARGET_IMAGE_MODEL)

        # We reverse the url name here

        if image_model_is_default:
            return

        conflict_config = []
        upload_handler_url_is_default = (
            self.upload_handler_url
            == get_url_from_str(defaults.DEFAULT_UPLOAD_HANDLER_URL_NAME,
                                require_urlconf_ready=True))

        if upload_handler_url_is_default:
            conflict_config.append(
                {"param": "upload_handler_url",
                 "value": self.upload_handler_url})

        if not self.disable_fetch:
            fetch_request_url_is_default = (
                self.fetch_request_url
                == get_url_from_str(defaults.DEFAULT_FETCH_URL_NAME,
                                    require_urlconf_ready=True))
            if fetch_request_url_is_default:
                conflict_config.append(
                    {"param": "fetch_request_url",
                     "value": self.fetch_request_url})

        if not conflict_config:
            return

        widget_is_servicing = getattr(self, "widget_is_servicing")
        msgs = ["'%(obj)s' is using '%(used_model)s' "
                "instead of built-in '%(default_model)s', while "
                % {"obj": widget_is_servicing,
                   "used_model": target_image_model,
                   "default_model": defaults.DEFAULT_TARGET_IMAGE_MODEL}
                ]

        for cc in conflict_config:
            msgs.append(
                "'%(param)s' is using built-in value '%(value)s', " % cc)

        msgs.append(
            "which use built-in '%(default_model)s'. You need to write "
            "your own views for your image model." % {
                "default_model": defaults.DEFAULT_TARGET_IMAGE_MODEL
            })

        msg = "".join(msgs)
        raise ImproperlyConfigured(msg)

    class Media:
        js = tuple(conf.JS)
        css = {'all': tuple(conf.CSS)}

    @property
    def is_hidden(self):
        return False

    def render(self, name, value, attrs=None, renderer=None):
        self.set_and_check_urls()

        context = {
            'input_string': super().render(name, value, attrs, renderer),
            'name': name,
            'multiple': self.multiple and 1 or 0,
            'thumbnail_size': str(self.thumbnail_size),
            'prompt_alert_on_window_reload_if_changed':
                conf.PROMPT_ALERT_ON_WINDOW_RELOAD_IF_CHANGED
        }

        # Do not fill in empty value to hidden inputs
        if value:
            context["pks"] = json.loads(value)
            context["fetch_request_url"] = self.fetch_request_url

        _context = self.get_context(name, value, attrs)

        if (_context["widget"]["attrs"].get("disabled", False)
                or _context["widget"]["attrs"].get("readonly")):
            context["uploader_disabled"] = True
        else:
            context.update({
                "upload_handler_url": self.upload_handler_url,
                "accepted_mime_types": self.options["accepted_mime_types"],
                "disable_server_side_crop": self.disable_server_side_crop
            })
        context["widget"] = _context["widget"]

        # Set blueimp/jQuery-File-Upload
        # https://github.com/blueimp/jQuery-File-Upload/wiki/Options
        max_number_of_images = (
            getattr(self, "max_number_of_images", None))
        if not max_number_of_images:
            self.ui_options.pop("maxNumberOfFiles", None)
        else:
            self.ui_options["maxNumberOfFiles"] = max_number_of_images

        _width, _height = self.thumbnail_size.split("x")
        self.ui_options.update(
            {"previewMaxWidth": _width,
             "previewMaxHeight": _height,
             "hiddenFileInput": "'.%s'" % conf.FILES_FIELD_CLASS_NAME,
             })

        context["jquery_fileupload_ui_options"] = (
            convert_dict_to_plain_text(self.ui_options, 16))

        return renderer.render(self.template, context)
