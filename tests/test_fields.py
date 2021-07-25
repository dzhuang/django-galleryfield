import json
from django import forms
from django.forms import ValidationError
from django.test import SimpleTestCase, TestCase

from gallery.fields import GalleryFormField

from demo.models import DemoGallery
from tests.factories import DemoGalleryFactory


class DemoTestGalleryForm(forms.ModelForm):
    class Meta:
        model = DemoGallery
        fields = ["images"]


IMAGE_DATA = [{
    "url": "/media/images/abcd.jpg",
    "thumbnailurl": "/media/cache/a6/ee/abcdefg.jpg",
    "name": "abcd.jpg", "size": "87700", "pk": 1,
    "deleteurl": "javascript:void(0)"}]


class GalleryFieldTest(TestCase):
    def test_form_save(self):
        form = DemoTestGalleryForm(
            data={"images_0": json.dumps(IMAGE_DATA),
                  "images_1": ''})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(
            json.loads(DemoGallery.objects.first().images)[0]["url"],
            IMAGE_DATA[0]["url"])

    def test_form_add_images(self):
        instance = DemoGalleryFactory.create()
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(len(json.loads(DemoGallery.objects.first().images)), 1)

        form = DemoTestGalleryForm(
            data={"images_0": json.dumps(IMAGE_DATA), "images_1": ''},
            instance=instance
        )
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(DemoGallery.objects.count(), 1)
        new_images = json.loads(DemoGallery.objects.first().images)
        self.assertEqual(len(new_images), 2)
        self.assertEqual(new_images[0]["url"], IMAGE_DATA[0]["url"])

    def test_form_change_images(self):
        instance = DemoGalleryFactory.create()
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(len(json.loads(DemoGallery.objects.first().images)), 1)

        form = DemoTestGalleryForm(
            data={"images_0": json.dumps(IMAGE_DATA),
                  "images_1": instance.images},
            instance=instance
        )
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(DemoGallery.objects.count(), 1)
        new_images = json.loads(DemoGallery.objects.first().images)
        self.assertEqual(len(new_images), 1)
        self.assertEqual(new_images[0]["url"], IMAGE_DATA[0]["url"])

    def test_form_save_null(self):
        form = DemoTestGalleryForm(
            data={"images_0": '',
                  "images_1": ''},
        )
        form.fields["images"].required = False

        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(DemoGallery.objects.count(), 1)
        new_images = json.loads(DemoGallery.objects.first().images)
        self.assertEqual(len(new_images), 0)

    def test_form_replace_null(self):
        instance = DemoGalleryFactory.create()
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(len(json.loads(DemoGallery.objects.first().images)), 1)

        form = DemoTestGalleryForm(
            data={"images_0": '',
                  "images_1": instance.images},
            instance=instance
        )
        form.fields["images"].required = False

        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(DemoGallery.objects.count(), 1)
        new_images = json.loads(DemoGallery.objects.first().images)
        self.assertEqual(len(new_images), 0)

    def test_form_invalid(self):
        instance = DemoGalleryFactory.create()
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(len(json.loads(DemoGallery.objects.first().images)), 1)

        form = DemoTestGalleryForm(
            data={"images_0": '',
                  "images_1": instance.images},
            instance=instance
        )
        form.fields["images"].required = True

        self.assertFalse(form.is_valid())


class GalleryFormFieldTest(SimpleTestCase):

    def test_gallery_model_field_clean(self):
        field = GalleryFormField()
        form_data = [json.dumps(IMAGE_DATA), ['']]
        cleaned_data = field.clean(form_data)
        self.assertEqual(str(cleaned_data), str(json.dumps(IMAGE_DATA)))

    def test_gallery_model_field_clean_null_required(self):
        field = GalleryFormField(required=True)
        inputs = [
            '',
            ['', ''],
            ['', str(json.dumps(IMAGE_DATA))]
        ]

        msg = "'The submitted file is empty.'"

        for data in inputs:
            with self.subTest(data=data):
                with self.assertRaisesMessage(ValidationError, msg):
                    field.clean(data)

    def test_gallery_model_field_clean_null_not_required(self):
        field = GalleryFormField(required=False)
        inputs = [
            '',
            ['', '']
        ]

        for data in inputs:
            with self.subTest(data=data):
               self.assertEqual(json.loads(field.clean(data)), '')

    def test_gallery_model_field_clean_invalid_json(self):
        inputs = ['invalid-image']
        msg = "Enter a valid JSON."

        for required in [True, False]:
            with self.subTest(required=required):
                field = GalleryFormField(required=required)
                with self.assertRaisesMessage(ValidationError, msg):
                    field.clean(inputs)

    def test_gallery_model_field_clean_not_null_not_list(self):
        input_str = 'invalid-image'
        msg = "Enter a list of values."

        for required in [True, False]:
            with self.subTest(required=required):
                field = GalleryFormField(required=required)
                with self.assertRaisesMessage(ValidationError, msg):
                    field.clean(input_str)

    def test_gallery_model_field_clean_disabled(self):
        field = GalleryFormField(disabled=True)
        inputs = json.dumps(IMAGE_DATA)
        self.assertEqual(json.loads(field.clean(inputs)), inputs)
