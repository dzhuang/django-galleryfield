from django.test import SimpleTestCase, TestCase
from .mixins import UserCreateMixin


class GalleryWidgetViewTest(UserCreateMixin, TestCase):
    @classmethod
    def setUpTestData(cls):  # noqa
        super().setUpTestData()
        cls.user = cls.create_user()

    def test_upload(self):
        pass
