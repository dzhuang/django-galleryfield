# -*- coding: utf-8 -*-
import json

from django import forms
from django.urls import reverse_lazy

from . import conf
from .defaults import GALLERY_WIDGET_UI_DEFAULT_OPTIONS


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
    "js/jquery.fileupload-ui-extended.js",
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


class GalleryWidget(forms.MultiWidget):
    def __init__(
            self,
            target_image_model=conf.DEFAULT_TARGET_IMAGE_MODEL,
            image_field_name=conf.DEFAULT_TARGET_IMAGE_FIELD_NAME,
            creator_field_name=conf.DEFAULT_CREATOR_FIELD_NAME,

            upload_handler_url_name=conf.DEFAULT_UPLOAD_HANDLER_URL_NAME,
            upload_handler_url_args=None, upload_handler_url_kwargs=None,

            multiple=True,
            preview_size=conf.DEFAULT_THUMBNAIL_SIZE,
            template="gallery/widget.html",
            attrs=None, options=None,
            jquery_upload_ui_options=None,
            **kwargs):

        # If BootStrap is loaded, "hiddeninput" is added by BootStrap.
        # However, we need that css class to check changes of the form,
        # so we added it manually.
        widgets = (
            forms.HiddenInput(
                attrs={
                    "class": " ".join(
                        [conf.FILES_FIELD_CLASS_NAME, "hiddeninput"])}),
            forms.HiddenInput(
                attrs={
                    "class": " ".join(
                        [conf.DELETED_FIELD_CLASS_NAME, "hiddeninput"]),
                    "required": False
                })
        )

        super(GalleryWidget, self).__init__(widgets, attrs)

        self.target_image_model = target_image_model
        self.image_field_name = image_field_name
        self.multiple = multiple
        self.preview_size = preview_size
        self.template = template

        self.upload_handler_url = reverse_lazy(
            upload_handler_url_name, args=upload_handler_url_args or (),
            kwargs=upload_handler_url_kwargs or {})

        jquery_upload_ui_options = jquery_upload_ui_options or {}
        _jquery_upload_ui_options = GALLERY_WIDGET_UI_DEFAULT_OPTIONS.copy()
        _jquery_upload_ui_options.update(jquery_upload_ui_options)

        # https://github.com/blueimp/jQuery-File-Upload/wiki/Options#singlefileuploads
        _jquery_upload_ui_options.pop("singleFileUploads", None)

        _jquery_upload_ui_options.update(
            {"previewMaxWidth": preview_size,
             "previewMaxHeight": preview_size,
             "hiddenFileInput": "'.%s'" % conf.FILES_FIELD_CLASS_NAME,
             "hiddenDeletedInput": "'.%s'" % conf.DELETED_FIELD_CLASS_NAME,
             "target_image_model": "'%s'" % target_image_model,
             "image_field_name": "'%s'" % image_field_name,
             "creator_field_name": "'%s'" % creator_field_name,
             })

        self.ui_options = _jquery_upload_ui_options
        self.options = options and options.copy() or {}
        self.options.setdefault("accepted_mime_types", ['image/*'])

    class Media:
        js = tuple(_js for _js in js if _js)
        css = {'all': tuple(_css for _css in css if _css)}

    @property
    def is_hidden(self):
        return False

    def decompress(self, value):
        if value:
            return [value, '']
        return ['', '']

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        # Bug: https://forum.djangoproject.com/t/multivaluefield-subwidgets-required/1196/8  # noqa
        assert not context["widget"]["subwidgets"][1]["required"]
        context["widget"]["subwidgets"][1]["attrs"]["required"] = False
        return context

    def render(self, name, value, attrs=None, renderer=None):
        if not isinstance(value, list):
            value, __ = self.decompress(value)
            assert isinstance(value, str), type(value)
        else:
            # This happens when submitted value contains non-empty delete_files
            value = json.dumps(value)

        context = {
            'input_string': super().render(name, value, attrs, renderer),
            'name': name,
            'multiple': self.multiple and 1 or 0,
            'preview_size': str(self.preview_size),
            "upload_handler_url": self.upload_handler_url,
            "accepted_mime_types": self.options["accepted_mime_types"],
        }

        def is_value_empty(_value):
            if not _value:
                return True
            if isinstance(_value, str):
                if _value == "[]":
                    return True
            if isinstance(_value, list):
                if _value == ["[]", '', '']:
                    return True
            return False

        # Do not fill in empty value to hidden inputs
        if not is_value_empty(value):
            context["files"] = value

        _context = self.get_context(name, value, attrs)

        if (_context["widget"]["attrs"].get("disabled", False)
                or _context["widget"]["attrs"].get("readonly") == "readonly"):
            context["uploader_disabled"] = True
        context["widget"] = _context["widget"]

        # Set blueimp/jQuery-File-Upload
        # https://github.com/blueimp/jQuery-File-Upload/wiki/Options
        from .utils import convert_dict_to_plain_text
        max_number_of_allowed_upload_file = self.ui_options.get("maxNumberOfFiles", 0)
        if not max_number_of_allowed_upload_file:
            self.ui_options.pop("maxNumberOfFiles", None)

        context["jquery_fileupload_ui_options"] = (
            convert_dict_to_plain_text(self.ui_options, 16))

        context["prompt_alert_on_window_reload_if_changed"] = (
            conf.PROMPT_ALERT_ON_WINDOW_RELOAD_IF_CHANGED)

        return renderer.render(self.template, context)
