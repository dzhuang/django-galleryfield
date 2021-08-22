import json

from django import forms
from django.core.exceptions import ImproperlyConfigured

from galleryfield import conf, defaults
from galleryfield.utils import (convert_dict_to_plain_text,
                                get_formatted_thumbnail_size, get_url_from_str,
                                logger)


class GalleryWidget(forms.HiddenInput):
    """This is the default widget used by :class:`galleryfield.fields.GalleryFormField`.

    :param upload_handler_url: An URL name or an url of the upload handler
           view used by the widget instance, defaults to `None`. If `None`, 
           upload ui won't show upload buttons. When the parent 
           :class:`galleryfield.fields.GalleryFormField` is used by
           a :class:`galleryfield.fields.GalleryField`, that url will be auto-configured,
           with the value in the form of ``model_name-upload`` in lower case.
           For example, if ``target_model`` is ``myapp.MyImageModel``, then
           the `upload_handler_url` is auto-configured to ``myimagemodel-upload``.
           You need to make sure you had that URL name in your URL_CONF and 
           related views exists.
    :type upload_handler_url: str, optional
    :param fetch_request_url: An URL name or an url for fetching the existing
           images in the gallery instance, defaults to `None`. If `None`, 
           upload ui won't load existing images. Like ``upload_handler_url``,
           this param will be auto-configured in the form of ``model_name-fetch``.
    :type fetch_request_url: str, optional
    :param multiple: Whether allow to select multiple image files in the 
           file picker.
    :type multiple: bool, optional
    :param thumbnail_size: The thumbnail size (both width and height), defaults 
           to ``defaults.DEFAULT_THUMBNAIL_SIZE``, which can be overridden by
           ``settings.DJANGO_GALLERY_FIELD_CONFIG["thumbnails"]["size"]``.
           The value can be set after the widget is initialized.
    :type thumbnail_size: int, optional
    :param template: The path of template which is used to render the widget.
           defaults to ``galleryfield/widget.html``, which support template 
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
    :param jquery_file_upload_ui_options: The default template is using 
           blueimp/jQuery-File-Upload package to render the ui and dealing with
           AJAX upload. This param can be used to set the options. See
           `jQuery-File-Upload Wiki <https://github.com/blueimp/jQuery-File-Upload/wiki/Options>`_
           for all the available options. The default options can be 
           seen in ``defaults.GALLERY_WIDGET_UI_DEFAULT_OPTIONS``. Notice that
           ``maxNumberOfFiles`` is overridden by the ``max_number_of_images`` param
           when initializing :class:`galleryfield.fields.GalleryFormField`, and
           ``previewMaxWidth`` and ``previewMaxHeight`` are overridden by
           param ``thumbnail_size``.
    :type jquery_file_upload_ui_options: dict, optional
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
            template="galleryfield/widget.html",
            attrs=None, options=None,
            jquery_file_upload_ui_options=None,
            disable_fetch=False,
            disable_server_side_crop=False,
            **kwargs):

        super(GalleryWidget, self).__init__(attrs)

        self.multiple = multiple
        self._thumbnail_size = get_formatted_thumbnail_size(thumbnail_size)
        self.template = template

        self.disable_fetch = disable_fetch
        self.disable_server_side_crop = disable_server_side_crop

        self.upload_handler_url = upload_handler_url

        self.fetch_request_url = (
            None if disable_fetch else fetch_request_url)

        self.jquery_file_upload_ui_options = jquery_file_upload_ui_options or {}

        self.options = options and options.copy() or {}
        self.options.setdefault("accepted_mime_types", ['image/*'])

    @property
    def thumbnail_size(self):
        return self._thumbnail_size

    @thumbnail_size.setter
    def thumbnail_size(self, value):
        self._thumbnail_size = get_formatted_thumbnail_size(value)

    @property
    def jquery_file_upload_ui_options(self):
        return (self._jquery_file_upload_ui_options
                or conf.JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS)

    @jquery_file_upload_ui_options.setter
    def jquery_file_upload_ui_options(self, options):
        if options is None:
            return
        if not isinstance(options, dict):
            raise ImproperlyConfigured(
                "%(obj)s: 'jquery_file_upload_ui_options' must be a dict" % {
                    "obj": self.__class__.__name__
                }
            )
        ju_settings = (
            conf.JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS.copy())
        ju_settings.update(options)

        if "maxNumberOfFiles" in ju_settings:
            logger.warning(
                "%(obj)s: 'maxNumberOfFiles' in 'jquery_file_upload_ui_options' "
                "will be overridden later by the formfield. You should set that "
                "value in the formfield it belongs to, e.g. \n"
                "self.fields['my_gallery_field'].max_number_of_images = %(value)s"
                % {"obj": self.__class__.__name__,
                   "value": str(ju_settings["maxNumberOfFiles"])}
            )

        if ("singleFileUploads" in ju_settings
                and str(ju_settings["singleFileUploads"]).lower() == "false"):
            logger.warning(
                "%(obj)s: 'singleFileUploads=False' in "
                "'jquery_file_upload_ui_options' is not allowed and will be "
                "ignored."
                % {"obj": self.__class__.__name__}
            )

        if "previewMaxWidth" in ju_settings or "previewMaxHeight" in ju_settings:
            logger.warning(
                "%(obj)s: 'previewMaxWidth' and 'previewMaxHeight' in "
                "'jquery_file_upload_ui_options' are ignored. You should set "
                "the value by the 'thumbnail_size' option, e.g., "
                "thumbnail_size='120x60'"
                % {"obj": self.__class__.__name__}
            )

        self._jquery_file_upload_ui_options = ju_settings

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

        if self.disable_fetch:
            self.fetch_request_url = None
        else:
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

        if self.fetch_request_url:
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

    def get_stringfied_jquery_file_upload_ui_options(self):
        # See blueimp/jQuery-File-Upload
        # https://github.com/blueimp/jQuery-File-Upload/wiki/Options

        # We copy the options as the actual context used in rendering
        # so as to avoid logger warnings
        ui_options = self.jquery_file_upload_ui_options.copy()

        # Remove the option (i.e., use default False)
        ui_options.pop("singleFileUploads", None)

        # Remove other options which we are using default but
        # don't allow user to change
        for option in ["fileInput", "formData"]:
            ui_options.pop(option, None)

        # Fixme: this is hardcoded
        ui_options["paramName"] = "'files[]'"

        # override maxNumberOfFiles
        ui_options.pop("maxNumberOfFiles", None)
        max_number_of_images = (
            getattr(self, "max_number_of_images", None))

        if max_number_of_images:
            ui_options["maxNumberOfFiles"] = max_number_of_images

        # override previewMaxWidth and previewMaxHeight

        _width, _height = self.thumbnail_size.split("x")
        ui_options.update(
            {"previewMaxWidth": _width,
             "previewMaxHeight": _height,

             # This is used as a CSS selector to fine the input field
             "hiddenFileInput": "'.%s'" % conf.FILES_FIELD_CLASS_NAME,
             })

        return convert_dict_to_plain_text(ui_options, indent=16)

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

        context["jquery_fileupload_ui_options"] = (
            self.get_stringfied_jquery_file_upload_ui_options())

        return renderer.render(template_name=self.template, context=context)
