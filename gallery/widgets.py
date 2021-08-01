import json

from django import forms
from django.urls import reverse_lazy

from gallery import conf
from gallery import defaults
from .utils import convert_dict_to_plain_text

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
            upload_handler_url_name=conf.DEFAULT_UPLOAD_HANDLER_URL_NAME,
            upload_handler_args=None,
            upload_handler_kwargs=None,
            fetch_request_url_name=conf.DEFAULT_FETCH_URL_NAME,
            fetch_request_args=None,
            fetch_request_kwargs=None,
            crop_request_url_name=conf.DEFAULT_CROP_URL_NAME,
            crop_request_args=None,
            crop_request_kwargs=None,
            multiple=True,
            preview_size=conf.DEFAULT_THUMBNAIL_SIZE,
            template="gallery/widget.html",
            attrs=None, options=None,
            jquery_upload_ui_options=None,
            **kwargs):

        super(GalleryWidget, self).__init__(attrs)

        self.multiple = multiple
        self.preview_size = preview_size
        self.template = template

        self._upload_handler_url_name = upload_handler_url_name
        self._fetch_request_url_name = fetch_request_url_name
        self._crop_request_url_name = crop_request_url_name

        self.upload_handler_url = reverse_lazy(
            upload_handler_url_name, args=upload_handler_args or (),
            kwargs=upload_handler_kwargs or {})

        self.fetch_request_url = None
        if fetch_request_url_name:
            self.fetch_request_url = reverse_lazy(
                fetch_request_url_name, args=fetch_request_args or (),
                kwargs=fetch_request_kwargs or {})

        self.crop_request_url = None
        if crop_request_url_name:
            self.crop_request_url = reverse_lazy(
                crop_request_url_name, args=crop_request_args or (),
                kwargs=crop_request_kwargs or {})

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

    def defaults_checks(self):
        image_model_str = getattr(self, "image_model", None)
        if not image_model_str:
            return

        image_model_is_default = (
                image_model_str == defaults.DEFAULT_TARGET_IMAGE_MODEL)
        upload_handler_url_name_is_default = (
            self._upload_handler_url_name == defaults.DEFAULT_UPLOAD_HANDLER_URL_NAME
        )
        fetch_request_url_name_is_default = (
            self._fetch_request_url_name == defaults.DEFAULT_FETCH_URL_NAME
        )
        crop_request_url_name_is_default = (
            self._crop_request_url_name == defaults.DEFAULT_CROP_URL_NAME
        )
        conflict_config = []
        if not image_model_is_default:
            if upload_handler_url_name_is_default:
                conflict_config.append(
                    {"param": "upload_handler_url_name",
                     "value": self._upload_handler_url_name})
            if fetch_request_url_name_is_default:
                conflict_config.append(
                    {"param": "fetch_request_url_name",
                     "value": self._fetch_request_url_name})
            if crop_request_url_name_is_default:
                conflict_config.append(
                    {"param": "crop_request_url_name",
                     "value": self._crop_request_url_name})

        if conflict_config:
            widget_belong = getattr(self, "widget_belong")
            msgs = ["'%(obj)s' is using '%(used_model)s' "
                    "instead of built-in '%(default_model)s', while "
                    % {"obj": widget_belong,
                       "used_model": image_model_str,
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
            if msg:
                raise RuntimeError(msg)

    class Media:
        js = tuple(_js for _js in js if _js)
        css = {'all': tuple(_css for _css in css if _css)}

    @property
    def is_hidden(self):
        return False

    def render(self, name, value, attrs=None, renderer=None):
        self.defaults_checks()

        # extra_attrs = {"style": "display:none"}
        # # extra_attrs = {}
        # extra_attrs.update(attrs)

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
                "crop_request_url": self.crop_request_url
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
