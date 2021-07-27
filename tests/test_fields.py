import json
from copy import deepcopy

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
    "thumbnailUrl": "/media/cache/a6/ee/abcdefg.jpg",
    "name": "abcd.jpg", "size": "87700", "pk": 1,
    "deleteUrl": "javascript:void(0)"}]


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

        self.assertTrue(form.is_valid(), form.errors)
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

    def test_gallery_form_field_clean(self):
        field = GalleryFormField()
        form_data = [json.dumps(IMAGE_DATA), '']
        cleaned_data = field.clean(form_data)
        self.assertEqual(str(cleaned_data), str(json.dumps(IMAGE_DATA)))

    def test_gallery_form_field_clean_null_required(self):
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

    def test_gallery_form_field_clean_null_not_required(self):
        field = GalleryFormField(required=False)
        inputs = [
            '',
            ['', '']
        ]

        for data in inputs:
            with self.subTest(data=data):
               self.assertEqual(json.loads(field.clean(data)), '')

    def test_gallery_form_field_clean_invalid_image_json(self):
        inputs = ['invalid-image']
        msg = "The submitted images are invalid."

        for required in [True, False]:
            with self.subTest(required=required):
                field = GalleryFormField(required=required)
                with self.assertRaisesMessage(ValidationError, msg):
                    field.clean(inputs)

    def test_gallery_form_field_clean_invalid_images_json(self):
        invalid_image_data = IMAGE_DATA[0].copy()
        invalid_image_data.pop("url")

        field = GalleryFormField(required=False)
        inputs = [

            # No url in each dict
            [json.dumps([invalid_image_data]), ''],
            ['', json.dumps([invalid_image_data])],

            # JSONDecodeError
            ['', 'invalid-image-data'],

            # list element not dicts
            ['', json.dumps(["url", "abcd"])],
            [json.dumps(["url", "abcd"]), ''],

            # data not list
            [json.dumps({"url": "abcd"}), ''],
            ['', json.dumps({"url": "abcd"})]
        ]
        msg = "The submitted images are invalid."

        for data in inputs:
            with self.subTest(data=data):
                with self.assertRaisesMessage(ValidationError, msg):
                    field.clean(data)

    def test_gallery_form_field_clean_not_null_not_list(self):
        input_str = 'invalid-image'
        msg = "The submitted images are invalid."

        for required in [True, False]:
            with self.subTest(required=required):
                field = GalleryFormField(required=required)
                with self.assertRaisesMessage(ValidationError, msg):
                    field.clean(input_str)

    def test_gallery_form_field_clean_disabled_invalid(self):
        field = GalleryFormField(disabled=True)
        input_str = 'invalid-image'
        msg = "The submitted images are invalid."

        with self.assertRaisesMessage(ValidationError, msg):
            field.clean(input_str)

    def test_gallery_form_field_clean_disabled(self):
        field = GalleryFormField(disabled=True)
        inputs = json.dumps(IMAGE_DATA)
        self.assertEqual(json.loads(field.clean(inputs)), inputs)

    def test_gallery_form_field_assign_max_number_of_images(self):
        field = GalleryFormField(required=False)
        max_number_of_images_list = [
            0,
            "1",
            "123",
            1234,
            None
        ]

        for n in max_number_of_images_list:
            with self.subTest(max_number_of_images=n):
                field.max_number_of_images = n
                if n is not None:
                    self.assertEqual(field.max_number_of_images, int(n))
                    self.assertEqual(field.widget.max_number_of_images, int(n))
                else:
                    self.assertIsNone(field.max_number_of_images)
                    self.assertIsNone(field.widget.max_number_of_images)

    def test_gallery_form_field_assign_max_number_of_images_invalid(self):
        field = GalleryFormField(required=False)
        max_number_of_images_list = [
            -1,
            "-1",
            "abc",
            object,
        ]

        for n in max_number_of_images_list:
            with self.subTest(max_number_of_images=n):
                with self.assertRaises(TypeError):
                    field.max_number_of_images = n

    def test_gallery_form_field_clean_max_number_of_images_exceeded(self):
        field = GalleryFormField()
        n = 1
        field.max_number_of_images = n

        second_image_info = {
            "url": "/media/images/cdef.jpg",
            "thumbnailUrl": "/media/cache/a6/ee/cdef.jpg",
            "name": "cdef.jpg", "size": "20000", "pk": 2,
            "deleteUrl": "javascript:void(0)"}
        image_data_with_2_images = deepcopy(IMAGE_DATA)
        image_data_with_2_images.append(second_image_info)

        msg = "Number of images exceeded, only %i allowed" % n

        with self.assertRaisesMessage(ValidationError, msg):
            field.clean([json.dumps(image_data_with_2_images), ''])

    def test_gallery_form_field_clean_max_number_of_images_not_exceeded(self):
        field = GalleryFormField()
        field.max_number_of_images = 1

        form_data = [json.dumps(IMAGE_DATA), '']
        cleaned_data = field.clean(form_data)
        self.assertEqual(str(cleaned_data), str(json.dumps(IMAGE_DATA)))

    def test_gallery_form_field_clean_max_number_of_images_zero(self):
        # zero means not limited
        field = GalleryFormField()
        field.max_number_of_images = 0

        form_data = [json.dumps(IMAGE_DATA), '']
        cleaned_data = field.clean(form_data)
        self.assertEqual(str(cleaned_data), str(json.dumps(IMAGE_DATA)))