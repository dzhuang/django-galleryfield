# -*- coding: utf-8 -*-
from django.forms.widgets import HiddenInput, TextInput
from django.utils.safestring import mark_safe
from django.template import loader
from django.urls import reverse
from django.utils.encoding import force_text

from .configs import (
    JQUERY_JS_PATH, BOOTSTRAP_JS_PATH, BOOTSTRAP_CSS_PATH, GALLERY_EXTRA_JS, GALLERY_EXTRA_CSS,
    GALLERY_UPLOAD_HANDLER_URL_NAME)


js = [
    JQUERY_JS_PATH,
    'js/vendor/jquery.ui.widget.js',
    'js/tmpl.min.js',
    "js/load-image.min.js",
    "js/canvas-to-blob.min.js",
    BOOTSTRAP_JS_PATH,
    'js/jquery.blueimp-gallery.min.js',
    "js/jquery.iframe-transport.js",
    'js/jquery.fileupload.js',
    "js/jquery.fileupload-process.js",
    "js/jquery.fileupload-image.js",
    "js/jquery.fileupload-audio.js",
    "js/jquery.fileupload-video.js",
    "js/jquery.fileupload-validate.js",
    "js/jquery.fileupload-ui.js",
] + GALLERY_EXTRA_JS


css = [
    BOOTSTRAP_CSS_PATH,
    'css/blueimp-gallery.css',
    "css/jquery.fileupload.css",
    "css/jquery.fileupload-ui.css",
] + GALLERY_EXTRA_CSS


class GalleryWidget(TextInput):
    gallery_template_name = "gallery/widget.html"

    class Media:
        js = tuple(_js for _js in js if _js)
        css = {'all': tuple(_css for _css in css if _css)}

    def __init__(self, upload_handler_url_name=None, attrs=None, options=None,
                 upload_handler_url_args=None, upload_handler_url_kwargs=None):
        super(GalleryWidget, self).__init__(attrs)

        upload_handler_url_name = (
                upload_handler_url_name or GALLERY_UPLOAD_HANDLER_URL_NAME)

        self.upload_handler_url = reverse(
            upload_handler_url_name, args=upload_handler_url_args or (),
            kwargs=upload_handler_url_kwargs or {})
        self.options = options and options.copy() or {}
        self.options.setdefault("accepted_mime_types", ['image/*'])

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)

        if (context["widget"]["attrs"].get("disabled", False)
                or context["widget"]["attrs"].get("readonly") == "readonly"):
            context["uploader_disabled"] = True

        context.update({
            "upload_handler_url": self.upload_handler_url,
            "accepted_mime_types": self.options["accepted_mime_types"],
        })

        uploader_html = loader.get_template(self.gallery_template_name).render(context)

        input_html = HiddenInput().render(name, value, attrs, renderer)

        return mark_safe(force_text(uploader_html + input_html))
