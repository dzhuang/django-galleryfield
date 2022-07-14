import os

from django.test import TestCase

from demo_custom.models import CustomImage
from tests import factories
from tests.mixins import UserCreateMixin
from tests.utils import remove_upload_directory


class CustomDemoTest(UserCreateMixin, TestCase):
    @classmethod
    def setUpTestData(cls):  # noqa
        super().setUpTestData()
        cls.user = cls.create_user()

    def setUp(self) -> None:
        factories.UserFactory.reset_sequence()
        factories.CustomImageFactory.reset_sequence()
        factories.CustomGalleryFactory.reset_sequence()
        remove_upload_directory()

    # {{{ test remove image (instance) when removed from gallery in CustomGallery

    def test_update_gallery_with_image_removed(self):
        gallery = factories.CustomGalleryFactory.create(
            number_of_images=5, creator=self.user, user=self.user)

        first_image = CustomImage.objects.first()
        first_image_path = first_image.photo.path
        self.assertTrue(os.path.isfile(first_image_path))

        # Remove the first image
        gallery.images = gallery.images[1:]
        gallery.save()

        self.assertEqual(CustomImage.objects.count(), 4)
        self.assertFalse(os.path.isfile(first_image_path))

    def test_update_gallery_with_image_instance_not_removed(self):
        gallery = factories.CustomGalleryFactory.create(
            number_of_images=5, creator=self.user, user=self.user
        )

        first_image = CustomImage.objects.first()
        first_image_path = first_image.photo.path
        self.assertTrue(os.path.isfile(first_image_path))

        # another gallery with first image as member
        factories.CustomGalleryFactory.create(
            photos=[first_image], creator=self.user
        )

        # Remove the first image
        gallery.images = gallery.images[1:]
        gallery.save()

        self.assertEqual(CustomImage.objects.count(), 5)
        self.assertTrue(os.path.isfile(first_image_path))

    def test_update_gallery_with_image_instance_removed_but_file_persist(self):
        gallery = factories.CustomGalleryFactory.create(
            number_of_images=5, creator=self.user, user=self.user
        )

        first_image = CustomImage.objects.first()
        cloned_image = CustomImage.objects.first()
        cloned_image.pk = None
        cloned_image.save()

        first_image_path = first_image.photo.path
        self.assertTrue(os.path.isfile(first_image_path))
        self.assertEqual(first_image_path, cloned_image.photo.path)

        # Remove the first image
        gallery.images = gallery.images[1:]
        gallery.save()

        self.assertEqual(CustomImage.objects.count(), 5)
        self.assertTrue(os.path.isfile(first_image_path))

    # }}}
