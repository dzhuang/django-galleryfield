import json
import re

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch

from gallery import conf, defaults
from gallery.utils import get_url_from_str, convert_dict_to_plain_text

NoReverseMatch_EXCEPTION_STR_RE = re.compile("Reverse for '(.+)' not found")

js = [
    conf.JQUERY_JS_PATH,
    'vendor/jquery-ui-dist/jquery-ui.min.js',
    'vendor/blueimp-file-upload/js/vendor/jquery.ui.widget.js',
    'vendor/blueimp-tmpl/js/tmpl.min.js',
    "vendor/blueimp-load-image/js/load-image.all.min.js",
    "vendor/blueimp-canvas-to-blob/js/canvas-to-blob.js",
    conf.BOOTSTRAP_JS_PATH,
    "vendor/jquery.iframe-transport/jquery.iframe-transport.js",
    'vendor/blueimp-file-upload/js/jquery.fileupload.js',
    'vendor/blueimp-file-upload/js/jquery.fileupload-process.js',
    'vendor/blueimp-file-upload/js/jquery.fileupload-image.js',
    'vendor/blueimp-file-upload/js/jquery.fileupload-audio.js',
    'vendor/blueimp-file-upload/js/jquery.fileupload-video.js',
    'vendor/blueimp-file-upload/js/jquery.fileupload-validate.js',
    'vendor/blueimp-file-upload/js/jquery.fileupload-ui.js',
    'vendor/blueimp-gallery/js/jquery.blueimp-gallery.min.js',
    "vendor/cropper/dist/cropper.min.js",
    "js/jquery.fileupload-ui-gallery-widget.js",
] + conf.EXTRA_JS

css = [
          conf.BOOTSTRAP_CSS_PATH,
          'vendor/jquery-ui-dist/jquery-ui.theme.min.css',
          'vendor/blueimp-gallery/css/blueimp-gallery.min.css',
          "vendor/blueimp-file-upload/css/jquery.fileupload.css",
          "vendor/blueimp-file-upload/css/jquery.fileupload-ui.css",
          'vendor/font-awesome/css/font-awesome.min.css',
          "vendor/cropper/dist/cropper.min.css",
] + conf.EXTRA_CSS


class GalleryWidget(forms.HiddenInput):
    def __init__(
            self,
            upload_handler_url=None,
            fetch_request_url=None,
            multiple=True,
            preview_size=conf.DEFAULT_THUMBNAIL_SIZE,
            template="gallery/widget.html",
            attrs=None, options=None,
            jquery_upload_ui_options=None,
            disable_fetch=False,
            disable_server_side_crop=False,
            **kwargs):

        super(GalleryWidget, self).__init__(attrs)

        self.multiple = multiple
        self.preview_size = preview_size
        self.template = template

        self.disable_fetch = disable_fetch
        self.disable_server_side_crop = disable_server_side_crop

        self._upload_handler_url = get_url_from_str(upload_handler_url)

        self._fetch_request_url = (
            None if disable_fetch else get_url_from_str(fetch_request_url))

        jquery_upload_ui_options = jquery_upload_ui_options or {}
        _jquery_upload_ui_options = defaults.GALLERY_WIDGET_UI_DEFAULT_OPTIONS.copy()
        _jquery_upload_ui_options.update(jquery_upload_ui_options)

        # https://github.com/blueimp/jQuery-File-Upload/wiki/Options#singlefileuploads
        _jquery_upload_ui_options.pop("singleFileUploads", None)
        _jquery_upload_ui_options.pop("singleFileUploads", None)

        _jquery_upload_ui_options.update(
            {"previewMaxWidth": preview_size,
             "previewMaxHeight": preview_size,
             "hiddenFileInput": "'.%s'" % conf.FILES_FIELD_CLASS_NAME,
             })

        self.ui_options = _jquery_upload_ui_options
        self.options = options and options.copy() or {}
        self.options.setdefault("accepted_mime_types", ['image/*'])

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

    def check_urls(self):
        # Here we validate the urls and check the potential conflicts of init params
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
        try:
            upload_handler_url_is_default = (
                self.upload_handler_url
                == get_url_from_str(defaults.DEFAULT_UPLOAD_HANDLER_URL_NAME,
                                    require_urlconf_ready=True))
        except NoReverseMatch as e:

            raise ImproperlyConfigured(
                "'upload_handler_url' is invalid: %s is neither "
                "a valid url nor a valid url name."
                % re.match(NoReverseMatch_EXCEPTION_STR_RE, str(e)).groups()[0])

        if upload_handler_url_is_default:
            conflict_config.append(
                {"param": "upload_handler_url",
                 "value": self.upload_handler_url})

        if not self.disable_fetch:
            try:
                fetch_request_url_is_default = (
                    self.fetch_request_url
                    == get_url_from_str(defaults.DEFAULT_FETCH_URL_NAME,
                                        require_urlconf_ready=True))
            except NoReverseMatch as e:
                raise ImproperlyConfigured(
                    "'fetch_request_url' is invalid: %s is neither "
                    "a valid url nor a valid url name."
                    % re.match(NoReverseMatch_EXCEPTION_STR_RE, str(e)).groups()[0])

            if fetch_request_url_is_default:
                conflict_config.append(
                    {"param": "fetch_request_url",
                     "value": self.fetch_request_url})

        if not conflict_config:
            return

        widget_belongs_to = getattr(self, "widget_belongs_to")
        msgs = ["'%(obj)s' is using '%(used_model)s' "
                "instead of built-in '%(default_model)s', while "
                % {"obj": widget_belongs_to,
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
        js = tuple(_js for _js in js if _js)
        css = {'all': tuple(_css for _css in css if _css)}

    @property
    def is_hidden(self):
        return False

    def render(self, name, value, attrs=None, renderer=None):
        self.check_urls()

        context = {
            'input_string': super().render(name, value, attrs, renderer),
            'name': name,
            'multiple': self.multiple and 1 or 0,
            'preview_size': str(self.preview_size),
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

        context["jquery_fileupload_ui_options"] = (
            convert_dict_to_plain_text(self.ui_options, 16))

        return renderer.render(self.template, context)
