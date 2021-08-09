import json

from django.urls import reverse
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.staticfiles.finders import find
from django.utils.http import urlencode

from tests.mixins import UserCreateMixin
from tests.utils import (
    get_upload_file_path, test_media_root, remove_upload_directory)
from tests import factories

from gallery import defaults
from gallery.models import BuiltInGalleryImage


@override_settings(MEDIA_ROOT=test_media_root)
class GalleryWidgetViewTest(UserCreateMixin, TestCase):
    @classmethod
    def setUpTestData(cls):  # noqa
        super().setUpTestData()
        cls.user = cls.create_user()

    def setUp(self) -> None:
        factories.UserFactory.reset_sequence()
        factories.BuiltInGalleryImageFactory.reset_sequence()
        factories.DemoGalleryFactory.reset_sequence()

        self.c.logout()
        super().setUp()
        remove_upload_directory()

    @staticmethod
    def get_form_view_url():
        return reverse("gallery")

    @staticmethod
    def get_upload_url():
        return reverse(defaults.DEFAULT_UPLOAD_HANDLER_URL_NAME)

    @staticmethod
    def get_fetch_url(params=None):
        url = reverse(defaults.DEFAULT_FETCH_URL_NAME)
        params = params or {}
        if params:
            url += "?" + urlencode(params)
        return url

    @staticmethod
    def get_crop_url(pk):
        return reverse(defaults.DEFAULT_CROP_URL_NAME, kwargs={"pk": pk})

    @staticmethod
    def _get_crop_post_data(
            cropped_result=None,
            preview_size=defaults.DEFAULT_THUMBNAIL_SIZE):
        data = {}
        if cropped_result:
            data.update({"crop_result": cropped_result})
        if preview_size:
            data.update({"preview_size": preview_size})

        return data

    @staticmethod
    def get_cropped_result(**kwargs):
        data = {}
        for v in ["x", "y", "width", "height", "rotate"]:
            value = kwargs.get(v)
            if value is not None:
                data[v] = value

        return json.dumps(data)

    def test_upload(self):
        self.c.force_login(self.user)
        resp = self.c.get(self.get_form_view_url())
        self.assertEqual(resp.status_code, 200)

    def test_upload_invalid_file_type(self):
        self.c.force_login(self.user)
        self.c.get(self.get_form_view_url())
        file = get_upload_file_path("test_file.pdf")

        with open(file, "rb") as fp:
            resp = self.c.post(
                self.get_upload_url(),
                data={"files[]": fp}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 400)

        expected_error = ("Upload a valid image. The file you uploaded "
                          "was either not an image or a corrupted image.")
        errors = json.loads(resp.content)["errors"]["image"]
        self.assertIn(expected_error, errors)
        self.assertEqual(BuiltInGalleryImage.objects.count(), 0)

    def upload_file(self, user, file_obj, force_login=True):
        if force_login:
            self.c.force_login(user)
        with open(file_obj, "rb") as fp:
            resp = self.c.post(
                self.get_upload_url(),
                data={"files[]": fp}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        return resp

    def test_upload_success(self):
        resp = self.upload_file(self.user, find("demo/screen_upload.png"))
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(BuiltInGalleryImage.objects.count(), 1)

    def test_upload_not_logged_in(self):
        resp = self.upload_file(self.user, find("demo/screen_upload.png"),
                                force_login=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(BuiltInGalleryImage.objects.count(), 0)

    def test_fetch(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        # This was used to make sure only images in the specific
        # gallery will be fetched.
        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=2,
            shuffle=True)

        def get_fetched_result():
            resp = self.c.get(self.get_fetch_url(
                params={"pks": list(gallery.images)}),
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(resp.status_code, 200)
            resp_image_list = [file["pk"]
                               for file in json.loads(resp.content)["files"]]
            return resp_image_list

        image_list = list(gallery.images)

        self.c.force_login(self.user)
        self.assertEqual(image_list, get_fetched_result())

        self.c.force_login(self.superuser)
        self.assertEqual(image_list, get_fetched_result())

        another_user = self.create_user()
        self.c.force_login(another_user)
        self.assertEqual(len(get_fetched_result()), 0)

    def test_fetch_without_pks(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        self.c.force_login(self.user)
        resp = self.c.get(self.get_fetch_url(
            params={"not-pks": list(gallery.images)}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resp.status_code, 400)

    def test_fetch_pk_not_digit(self):
        self.c.force_login(self.user)
        resp = self.c.get(self.get_fetch_url(
            params={"pks": [1.1]}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resp.status_code, 400)

    def test_fetch_pk_decode_error(self):
        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        self.c.force_login(self.user)
        resp = self.c.get(self.get_fetch_url(
            params={"pks": "abcd"}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resp.status_code, 400)

    def test_fetch_pk_loaded_but_not_list(self):
        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        self.c.force_login(self.user)
        resp = self.c.get(self.get_fetch_url(
            params={"pks": '{"ab": "cd"}'}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resp.status_code, 400)

    def test_fetch_not_logged_in(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        resp = self.c.get(self.get_fetch_url(
            params={"not-pks": list(gallery.images)}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resp.status_code, 302)

    # def get_crop_post_data(self, **kwargs):
    #     default_result = {
    #         "x": 200, "y": 200, "width": 400,
    #         "height": 810, "rotate": -90}
    #     kwargs = kwargs or {}
    #     default_result.update(**kwargs)
    #     cropped = self.get_cropped_result(**default_result)
    #     data = self._get_crop_post_data(cropped_result=cropped)
    #     return data
    #
    # def get_crop_pk(self, idx):
    #     gallery = factories.DemoGalleryFactory.create(
    #         creator=self.user, number_of_images=5, shuffle=True)
    #     pk = gallery.images[idx]
    #     return pk
    #
    # def get_default_crop_post_data(self, **kwargs):
    #     data = self.get_crop_post_data(**kwargs)
    #     return data
    #
    # def test_crop_success(self):
    #     pk = self.get_crop_pk(0)
    #     data = self.get_default_crop_post_data()
    #
    #     self.c.force_login(self.user)
    #     resp = self.c.post(self.get_crop_url(pk), data=data,
    #                        HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    #     self.assertEqual(resp.status_code, 200)
    #
    #     pk = self.get_crop_pk(1)
    #     data = self.get_default_crop_post_data()
    #     self.c.force_login(self.superuser)
    #     resp = self.c.post(self.get_crop_url(pk), data=data,
    #                        HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    #     self.assertEqual(resp.status_code, 200)
    #
    # def test_crop_png(self):
    #     self.upload_file(self.user, find("demo/screen_upload.png"))
    #     factories.DemoGalleryFactory.create(
    #         creator=self.user, images=[BuiltInGalleryImage.objects.first()])
    #     data = self.get_crop_post_data()
    #
    #     self.c.force_login(self.user)
    #     resp = self.c.post(self.get_crop_url(1), data=data,
    #                        HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    #     self.assertEqual(resp.status_code, 200)
    #
    # def test_crop_non_exist_image(self):
    #     data = self.get_crop_post_data()
    #
    #     self.c.force_login(self.user)
    #     resp = self.c.post(self.get_crop_url(100), data=data,
    #                        HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    #     self.assertEqual(resp.status_code, 404)
    #
    # def test_crop_cropResult_invalid(self):
    #     data = self.get_default_crop_post_data(x=None)
    #
    #     self.c.force_login(self.user)
    #     pk = self.get_crop_pk(1)
    #     resp = self.c.post(self.get_crop_url(pk), data=data,
    #                        HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    #     self.assertEqual(resp.status_code, 400)
    #
    # def test_crop_no_rotate(self):
    #     data = self.get_default_crop_post_data(rotate=0)
    #
    #     pk = self.get_crop_pk(1)
    #     self.c.force_login(self.user)
    #     resp = self.c.post(self.get_crop_url(pk), data=data,
    #                        HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    #     self.assertEqual(resp.status_code, 200, resp.content)
    #
    # def test_crop_io_error(self):
    #     # no actual image file
    #     gallery = factories.DemoGalleryFactory.create(creator=self.user)
    #     import os
    #     os.remove(gallery.images.objects.first().image.path)
    #
    #     pk = gallery.images.objects.first().pk
    #     data = self.get_crop_post_data()
    #     self.c.force_login(self.user)
    #     resp = self.c.post(self.get_crop_url(pk), data=data,
    #                        HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    #     self.assertEqual(resp.status_code, 400)
    #
    # def test_crop_permission_denied(self):
    #     pk = self.get_crop_pk(0)
    #     data = self.get_default_crop_post_data()
    #
    #     another_user = self.create_user()
    #     self.c.force_login(another_user)
    #     resp = self.c.post(self.get_crop_url(pk), data=data,
    #                        HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    #     self.assertEqual(resp.status_code, 403)
    #
    # def test_crop_not_logged_in(self):
    #     pk = self.get_crop_pk(0)
    #     data = self.get_default_crop_post_data()
    #
    #     resp = self.c.post(self.get_crop_url(pk), data=data,
    #                        HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    #     self.assertEqual(resp.status_code, 302)
