import json
from django import forms
from django.forms.renderers import DjangoTemplates
from django.utils.safestring import mark_safe
from django.test import SimpleTestCase
from django.urls import reverse

from gallery.fields import GalleryFormField
from gallery.widgets import GalleryWidget
from gallery import conf


class GalleryWidgetTest(SimpleTestCase):
    @staticmethod
    def _get_rendered_field_html(field, print_output=False):
        class Form(forms.Form):
            f = field

        haystack = str(Form()['f'])
        if print_output:
            print(haystack)
        return haystack

    def assertFieldRendersIn(self, field, needle, strict=False, print_output=False):
        haystack = self._get_rendered_field_html(field, print_output)
        assert_in = self.assertInHTML if not strict else self.assertIn
        assert_in(needle, haystack)

    def assertFieldRendersNotIn(self, field, needle, print_output=False):
        haystack = self._get_rendered_field_html(field, print_output)
        self.assertNotIn(needle, haystack)

    def test_widget(self):
        field = GalleryFormField()
        self.assertIsInstance(field.widget, GalleryWidget)

    def test_required_widget_render(self):
        f = GalleryFormField(required=True)
        self.assertFieldRendersIn(
            f, '<input type="hidden" name="f_0"'
               ' class="django-gallery-widget-files-field'
               ' hiddeninput" required id="id_f_0">'
               '<input type="hidden" name="f_1"'
               ' class="django-gallery-widget-deleted-field'
               ' hiddeninput" id="id_f_1">')

        f = GalleryFormField(required=False)
        self.assertFieldRendersIn(
            f, '<input type="hidden" name="f_0"'
               ' class="django-gallery-widget-files-field'
               ' hiddeninput" id="id_f_0">'
               '<input type="hidden" name="f_1"'
               ' class="django-gallery-widget-deleted-field'
               ' hiddeninput" id="id_f_1">')

    def _render_widget(self, widget, name, value, attrs=None, **kwargs):
        django_renderer = DjangoTemplates()
        print_output = kwargs.pop("print_output", False)
        output = widget.render(name, value, attrs=attrs,
                               renderer=django_renderer, **kwargs)
        if print_output:
            print(output)
        return output

    def check_in_html(self, widget, name, value, html, attrs=None,
                      strict=False, **kwargs):
        output = self._render_widget(widget, name, value, attrs=attrs, **kwargs)
        assert_in = self.assertIn if strict else self.assertInHTML
        if isinstance(html, str):
            html = [html]
        for _html in html:
            assert_in(_html, output)

    def check_not_in_html(self, widget, name, value, html, attrs=None, **kwargs):
        output = self._render_widget(widget, name, value, attrs=attrs, **kwargs)
        if isinstance(html, str):
            html = [html]
        for _html in html:
            self.assertNotIn(_html, output)

    def test_gallery_widget_render(self):
        widget = GalleryWidget()
        image_data = [{
            "url": "/media/images/abcd.jpg",
            "thumbnailurl": "/media/cache/a6/ee/abcdefg.jpg",
            "name": "abcd.jpg", "pk": "1", "size": "87700",
            "deleteurl": "javascript:void(0)"}]
        value = mark_safe(json.dumps(image_data))
        expected_result = (
            '<input type="hidden" name="image_0" '
            'value="[{"url": "/media/images/abcd.jpg", '
            '"thumbnailurl": "/media/cache/a6/ee/abcdefg.jpg", '
            '"name": "abcd.jpg", "pk": "1", "size": "87700", '
            '"deleteurl": "javascript:void(0)"}]" '
            'class="django-gallery-widget-files-field hiddeninput">')
        self.check_in_html(widget, "image", value, strict=True,
                           html=[expected_result])

    def test_gallery_widget_jquery_upload_options_max_number_of_files_overridden(self):  # noqa
        from random import randint
        max_number_of_file_ui_options_value = randint(1, 10)
        widget = GalleryWidget(
            jquery_upload_ui_options={
                "maxNumberOfFiles": max_number_of_file_ui_options_value})
        setattr(widget, "max_number_of_images", None)
        self.check_not_in_html(widget, "image", '', html="maxNumberOfFiles")

        widget = GalleryWidget(
            jquery_upload_ui_options={
                "maxNumberOfFiles": max_number_of_file_ui_options_value})
        setattr(widget, "max_number_of_images", 0)
        self.check_not_in_html(widget, "image", '', html="maxNumberOfFiles")

        max_number_of_file = randint(1, 10)
        widget = GalleryWidget(
            jquery_upload_ui_options={"maxNumberOfFiles": 0})

        setattr(widget, "max_number_of_images", max_number_of_file)
        expected_string = "maxNumberOfFiles: %i" % max_number_of_file
        self.check_in_html(widget, "image", '', strict=True, html=expected_string)

    def test_gallery_widget_preview_size(self):
        widget = GalleryWidget()
        expected_string = "previewMaxWidth: %i" % conf.DEFAULT_THUMBNAIL_SIZE
        self.check_in_html(widget, "image", '', strict=True, html=expected_string)

        widget = GalleryWidget(preview_size=130)
        expected_string = "previewMaxWidth: %i" % 130
        self.check_in_html(widget, "image", '', strict=True, html=expected_string)

    def test_gallery_widget_jquery_upload_options_None(self):
        widget = GalleryWidget()
        self.check_in_html(widget, "image", '', strict=True, html="disableImageResize")

        widget = GalleryWidget(
            jquery_upload_ui_options={"disableImageResize": None})
        self.check_not_in_html(widget, "image", '', html="disableImageResize")

    def test_gallery_widget_disabled(self):
        widget = GalleryWidget()
        file_upload_button = (
            '<input type="file" class="django-gallery-image-input" '
            'id="%(field_name)s-files" multiple accept="image/*" '
            'data-action="%(upload_handler_url)s">'
            % {"field_name": conf.DEFAULT_TARGET_IMAGE_FIELD_NAME,
               "upload_handler_url": reverse(conf.DEFAULT_UPLOAD_HANDLER_URL_NAME)}
        )
        self.check_in_html(
            widget, "image", '',
            html=[file_upload_button])

        widget.attrs["readonly"] = True
        self.check_not_in_html(
            widget, "image", '',
            # The css class of file input button
            html=["django-gallery-image-input"])

    def test_disabled_widget_render(self):
        f = GalleryFormField()
        self.assertFieldRendersIn(
            f, 'django-gallery-image-input', strict=True)

        f = GalleryFormField(disabled=True)
        self.assertFieldRendersNotIn(f, 'django-gallery-image-input')
