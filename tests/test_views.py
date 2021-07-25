from django.urls import reverse

from django.test import SimpleTestCase, TestCase
from tests.mixins import UserCreateMixin


class GalleryWidgetViewTest(UserCreateMixin, TestCase):
    @classmethod
    def setUpTestData(cls):  # noqa
        super().setUpTestData()
        cls.user = cls.create_user()

    def get_form_view_url(self):
        return reverse("gallery")

    def test_upload(self):
        self.c.force_login(self.user)
        resp = self.c.get(self.get_form_view_url())
        self.assertEqual(resp.status_code, 200)
