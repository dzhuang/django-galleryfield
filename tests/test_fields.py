import random
from unittest import mock

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.forms import ValidationError
from django.forms.widgets import Textarea
from django.test import TestCase
from django.test.utils import isolate_apps, override_settings

from demo.models import DemoGallery
from galleryfield.fields import GalleryField, GalleryFormField
from galleryfield.widgets import GalleryWidget
from tests import factories
from tests.factories import DemoGalleryFactory


class DemoTestGalleryModelForm(forms.ModelForm):
    class Meta:
        model = DemoGallery
        fields = ["images"]


class GalleryFieldTest(TestCase):
    def setUp(self) -> None:
        factories.UserFactory.reset_sequence()
        factories.BuiltInGalleryImageFactory.reset_sequence()
        factories.DemoGalleryFactory.reset_sequence()
        self.user = factories.UserFactory()
        super().setUp()

    def test_form_save(self):
        image = factories.BuiltInGalleryImageFactory(creator=self.user)
        form = DemoTestGalleryModelForm(data={"images": [image.pk]})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(DemoGallery.objects.count(), 1)

    def test_form_add_images(self):
        instance = factories.DemoGalleryFactory.create(creator=self.user)
        image2 = factories.BuiltInGalleryImageFactory(creator=self.user)
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(len(DemoGallery.objects.first().images), 1)

        form = DemoTestGalleryModelForm(
            data={"images": instance.images + [image2.pk]}, instance=instance
        )
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(DemoGallery.objects.count(), 1)
        new_images = DemoGallery.objects.first().images
        self.assertEqual(len(new_images), 2)

    def test_form_change_images(self):
        instance = DemoGalleryFactory.create(creator=self.user)
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(len(DemoGallery.objects.first().images), 1)
        image2 = factories.BuiltInGalleryImageFactory(creator=self.user)

        form = DemoTestGalleryModelForm(data={"images": [image2.pk]}, instance=instance)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(DemoGallery.objects.count(), 1)
        new_images = DemoGallery.objects.first().images
        self.assertEqual(len(new_images), 1)

    def test_form_save_null(self):
        form = DemoTestGalleryModelForm(
            data={"images": ""},
        )
        form.fields["images"].required = False

        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(DemoGallery.objects.count(), 1)
        new_images = DemoGallery.objects.first().images
        self.assertEqual(new_images, [])

    def test_form_replace_null(self):
        instance = DemoGalleryFactory.create(creator=self.user)
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(len(DemoGallery.objects.first().images), 1)

        form = DemoTestGalleryModelForm(data={"images": ""}, instance=instance)
        form.fields["images"].required = False

        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.assertEqual(DemoGallery.objects.count(), 1)
        new_images = DemoGallery.objects.first().images
        self.assertEqual(new_images, [])

    def test_form_invalid(self):
        instance = DemoGalleryFactory.create(creator=self.user)
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(len(DemoGallery.objects.first().images), 1)

        form = DemoTestGalleryModelForm(data={"images": ""}, instance=instance)
        form.fields["images"].required = True

        self.assertFalse(form.is_valid())


class GalleryFormFieldTest(TestCase):
    def setUp(self) -> None:
        factories.UserFactory.reset_sequence()
        factories.BuiltInGalleryImageFactory.reset_sequence()
        factories.DemoGalleryFactory.reset_sequence()
        self.user = factories.UserFactory()
        super().setUp()

    def test_gallery_form_field_clean_image_not_exist(self):
        field = GalleryFormField()
        form_data = [100]

        msg = "'The submitted file is empty.'"

        with self.assertRaisesMessage(ValidationError, msg):
            field.clean(form_data)

    def test_gallery_form_field_clean(self):
        image = factories.BuiltInGalleryImageFactory(creator=self.user)
        field = GalleryFormField()
        form_data = [image.pk]
        cleaned_data = field.clean(form_data)
        self.assertEqual(cleaned_data, form_data)

    def test_gallery_form_field_clean_null_required(self):
        field = GalleryFormField(required=True)
        inputs = [
            "",
            [],
        ]

        msg = "'The submitted file is empty.'"

        for data in inputs:
            with self.subTest(data=data):
                with self.assertRaisesMessage(ValidationError, msg):
                    field.clean(data)

    def test_gallery_form_field_clean_null_not_required(self):
        field = GalleryFormField(required=False)
        inputs = ["", None, "null", []]

        for data in inputs:
            with self.subTest(data=data):
                self.assertIsNone(field.clean(data))

    def test_gallery_form_field_clean_invalid_image_json(self):
        inputs = ["invalid-image"]
        msg = "The submitted images are invalid."

        for required in [True, False]:
            with self.subTest(required=required):
                field = GalleryFormField(required=required)
                with self.assertRaisesMessage(ValidationError, msg):
                    field.clean(inputs)

    def test_gallery_form_field_clean_not_null_not_list(self):
        input_str = "invalid-image"
        msg = "The submitted images are invalid."

        for required in [True, False]:
            with self.subTest(required=required):
                field = GalleryFormField(required=required)
                with self.assertRaisesMessage(ValidationError, msg):
                    field.clean(input_str)

    def test_gallery_form_field_clean_disabled_invalid(self):
        field = GalleryFormField(disabled=True)
        input_str = "invalid-image"
        msg = "The submitted images are invalid."

        with self.assertRaisesMessage(ValidationError, msg):
            field.clean(input_str)

    def test_gallery_form_field_assign_max_number_of_images(self):
        field = GalleryFormField(required=False)
        max_number_of_images_list = [0, "1", "123", 1234, None]

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

        images = factories.BuiltInGalleryImageFactory.create_batch(
            size=2, creator=self.user
        )

        msg = "Number of images exceeded, only %i allowed" % n

        with self.assertRaisesMessage(ValidationError, msg):
            field.clean([images[0].pk, images[1].pk])

    def test_gallery_form_field_clean_max_number_of_images_not_exceeded(self):
        field = GalleryFormField()
        field.max_number_of_images = 1

        image = factories.BuiltInGalleryImageFactory(creator=self.user)

        self.assertEqual(field.clean([image.pk]), [image.pk])

    def test_gallery_form_field_clean_max_number_of_images_zero(self):
        # zero means not limited
        field = GalleryFormField()
        field.max_number_of_images = 0

        images = factories.BuiltInGalleryImageFactory.create_batch(
            size=2, creator=self.user
        )

        data = [images[0].pk, images[1].pk]

        cleaned_data = field.clean(data)
        self.assertEqual(cleaned_data, data)

    def test_gallery_form_field_target_image_model_valid(self):
        GalleryFormField(target_model="tests.FakeValidImageModel")

    def test_gallery_form_field_target_image_model_invalid(self):
        with self.assertRaises(ImproperlyConfigured):
            GalleryFormField(target_model="tests.FakeInvalidImageModel1")

    @mock.patch("galleryfield.fields.logger.info")
    def test_gallery_form_field_target_image_model_configured_none(self, mock_log):
        GalleryFormField()
        self.assertEqual(mock_log.call_count, 1)

    @mock.patch("galleryfield.fields.logger.info")
    @override_settings(SILENCED_SYSTEM_CHECKS=["gallery_form_field.I001"])
    def test_gallery_form_field_target_image_model_configured_none_log_suppressed(
        self, mock_log
    ):  # noqa
        GalleryFormField()
        self.assertEqual(mock_log.call_count, 0)

    def test_gallery_form_field_changed_widget(self):
        max_number_of_images = 5
        field = GalleryFormField(
            target_model="tests.FakeValidImageModel",
            max_number_of_images=max_number_of_images,
            required=False,
        )
        old_widget = field.widget
        self.assertEqual(old_widget.max_number_of_images, max_number_of_images)

        # Before assigning to the formfield
        new_widget = GalleryWidget()
        self.assertNotEqual(new_widget.attrs, old_widget.attrs)
        self.assertFalse(hasattr(new_widget, "image_model"))
        self.assertFalse(hasattr(new_widget, "max_number_of_images"))

        # New widget will get updated
        field.widget = new_widget
        self.assertEqual(field.widget.max_number_of_images, max_number_of_images)
        self.assertEqual(field.widget.image_model, old_widget.image_model)
        self.assertEqual(field.widget.widget_is_servicing, field.__class__.__name__)
        self.assertEqual(field.widget.attrs, old_widget.attrs)
        self.assertEqual(field.widget.is_required, False)

    def test_gallery_form_field_textarea_widget_attribute_updated(self):
        form = DemoTestGalleryModelForm()

        max_n_of_images = random.randint(6, 10)

        # We set the max_number_of_images before change the widget,
        # to test after widget change, the attribute also exists
        form.fields["images"].max_number_of_images = max_n_of_images

        form.fields["images"].widget = Textarea()

        self.assertEqual(
            form.fields["images"].widget.max_number_of_images, max_n_of_images
        )

    def test_gallery_form_field_textarea_widget_max_number_of_images_validate(self):
        # create a gallery with 5 images pk randomized
        my_gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5, shuffle=True
        )

        form = DemoTestGalleryModelForm(data={"images": my_gallery.images})

        max_n_of_images = 2
        form.fields["images"].max_number_of_images = max_n_of_images
        form.fields["images"].widget = Textarea()

        self.assertFalse(form.is_valid())
        self.assertIn("Number of images exceeded, only 2 allowed", str(form.errors))

    def test_gallery_form_field_textarea_widget_value_render(self):
        # create a gallery with 5 images pk randomized
        my_gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5, shuffle=True
        )

        form = DemoTestGalleryModelForm(instance=my_gallery)

        image_pks = my_gallery.images
        self.assertIn(str(image_pks), form.as_table())

    def test_gallery_form_field_textarea_widget_value_sequence(self):
        # create a gallery with 5 images pk randomized
        my_gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5, shuffle=True
        )

        image_pks = my_gallery.images
        original_image_pks = image_pks[:]

        # Here we shuffle the image_pk, and submit it as the form data
        while True:
            random.shuffle(image_pks)
            if image_pks != original_image_pks:
                break

        form = DemoTestGalleryModelForm(data={"images": image_pks})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["images"], image_pks)


class GalleryFieldCheckTest(TestCase):
    def test_field_checks_valid(self):
        class MyModel(models.Model):
            field = GalleryField(target_model="tests.FakeInvalidImageModel1")

        model = MyModel()
        errors = model.check()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "gallery_field.E004")

    @isolate_apps("tests")
    def test_field_checks_use_default_target(self):
        class MyModel(models.Model):
            field = GalleryField()

        model = MyModel()
        errors = model.check()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "gallery_field.I001")

    @isolate_apps("tests")
    def test_field_checks_use_invalid_target(self):
        class MyModel(models.Model):
            field = GalleryField(target_model="non-exist.model")

        model = MyModel()
        errors = model.check()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "gallery_field.E002")

    @isolate_apps("tests")
    def test_field_checks_use_invalid_target_object(self):
        from tests.models import FakeValidImageModel

        class MyModel(models.Model):
            field = GalleryField(target_model=FakeValidImageModel)

        model = MyModel()
        errors = model.check()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "gallery_field.E001")

    @isolate_apps("tests")
    def test_field_checks_use_invalid_get_image_field_method(self):
        class MyModel(models.Model):
            field = GalleryField(target_model="tests.FakeInvalidImageModel5")

        model = MyModel()
        errors = model.check()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "gallery_field.E003")

    @isolate_apps("tests")
    def test_field_checks_use_get_image_field_method_not_callable(self):
        class MyModel(models.Model):
            field = GalleryField(target_model="tests.FakeInvalidImageModel4")

        model = MyModel()
        errors = model.check()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "gallery_field.E005")

    @isolate_apps("tests")
    def test_field_checks_use_get_image_field_method_not_imagefield(self):
        class MyModel(models.Model):
            field = GalleryField(target_model="tests.FakeInvalidImageModel3")

        model = MyModel()
        errors = model.check()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "gallery_field.E005")

    @isolate_apps("tests")
    # Here we are not loading "demo", while use MyImageModel
    @override_settings(INSTALLED_APPS=["galleryfield", "tests"])
    def test_field_checks_app_not_in_installed_apps(self):
        class MyModel(models.Model):
            field = GalleryField("demo.MyImageModel")

        # We want to make sure it won't raise error when initializing.
        model = MyModel()

        errors = model.check()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "gallery_field.E002")
        self.assertIn("LookupError", errors[0].msg)
