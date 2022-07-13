import json
import os
from unittest import mock

from django.contrib.staticfiles.finders import find
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.http import urlencode
from tests import factories
from tests.mixins import UserCreateMixin
from tests.utils import (get_upload_file_path, remove_upload_directory,
                         test_media_root)

from galleryfield import defaults
from galleryfield import image_views as built_in_views
from galleryfield.models import BuiltInGalleryImage


class ViewTestMixin(UserCreateMixin):
    @classmethod
    def setUpTestData(cls):  # noqa
        super().setUpTestData()
        cls.user = cls.create_user()

    def setUp(self) -> None:
        factories.UserFactory.reset_sequence()
        factories.BuiltInGalleryImageFactory.reset_sequence()
        factories.DemoGalleryFactory.reset_sequence()
        self.factory = RequestFactory()

        self.c.logout()
        super().setUp()
        remove_upload_directory()

    @staticmethod
    def get_demo_form_view_url():
        return reverse("gallery")

    @staticmethod
    def get_demo_upload_url():
        return reverse(defaults.DEFAULT_UPLOAD_URL_NAME)

    @staticmethod
    def get_demo_fetch_url(params=None):
        url = reverse(defaults.DEFAULT_FETCH_URL_NAME)
        params = params or {}
        if params:
            url += "?" + urlencode(params)
        return url

    @staticmethod
    def get_demo_crop_url(pk):
        return reverse(defaults.DEFAULT_CROP_URL_NAME, kwargs={"pk": pk})

    @staticmethod
    def _get_crop_post_data(
            cropped_result=None,
            thumbnail_size=defaults.DEFAULT_THUMBNAIL_SIZE):
        data = {}
        if cropped_result:
            data.update({"cropped_result": cropped_result})
        if thumbnail_size:
            data.update({"thumbnail_size": thumbnail_size})

        return data

    @staticmethod
    def get_cropped_result(**kwargs):
        data = {}
        for v in ["x", "y", "width", "height", "rotate"]:
            value = kwargs.get(v)
            if value is not None:
                data[v] = value

        return json.dumps(data)

    def demo_upload_file(self, user, file_obj, force_login=True, xml_request=True):
        if force_login:
            self.c.force_login(user)
        with open(file_obj, "rb") as fp:
            request_kwargs = {}
            if xml_request:
                request_kwargs["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
            resp = self.c.post(
                self.get_demo_upload_url(),
                data={"files[]": fp}, **request_kwargs)
        return resp

    def get_demo_crop_pk(self, idx):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5, shuffle=True)
        pk = gallery.images[idx]
        return pk

    def get_default_crop_post_data(self, **kwargs):
        data = self.get_crop_post_data(**kwargs)
        return data


@override_settings(MEDIA_ROOT=test_media_root)
class GalleryWidgetUploadViewTest(ViewTestMixin, TestCase):
    def test_get_gallery_page(self):
        self.c.force_login(self.user)
        resp = self.c.get(self.get_demo_form_view_url())
        self.assertEqual(resp.status_code, 200)

    def test_upload_invalid_file_type(self):
        self.c.force_login(self.user)
        file = get_upload_file_path("test_file.pdf")

        with open(file, "rb") as fp:
            resp = self.c.post(
                self.get_demo_upload_url(),
                data={"files[]": fp}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 400)

        expected_error = ("Upload a valid image. The file you uploaded "
                          "was either not an image or a corrupted image.")
        errors = json.loads(resp.content)["errors"]["image"]
        self.assertIn(expected_error, errors)
        self.assertEqual(BuiltInGalleryImage.objects.count(), 0)

    def test_upload_success(self):
        resp = self.demo_upload_file(self.user, find("demo/screen_upload.png"))
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(BuiltInGalleryImage.objects.count(), 1)

    def test_upload_fail_not_xml_request(self):
        resp = self.demo_upload_file(self.user, find("demo/screen_upload.png"),
                                     xml_request=False)
        self.assertEqual(resp.status_code, 403, resp.content)
        self.assertEqual(BuiltInGalleryImage.objects.count(), 0)

    def test_upload_not_logged_in(self):
        resp = self.demo_upload_file(self.user, find("demo/screen_upload.png"),
                                     force_login=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(BuiltInGalleryImage.objects.count(), 0)

    def test_cbv_target_model_not_configured(self):
        file = get_upload_file_path("test_file.pdf")

        with open(file, "rb") as fp:
            data = {"files[]": fp}
            request = self.factory.post(
                self.get_demo_upload_url(), data=data,
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        with self.assertRaises(ImproperlyConfigured) as cm:
            built_in_views.BuiltInImageCreateView.as_view(
                target_model=None)(request)

        expected_msg = ("Using BaseImageModelMixin (base class of "
                        "BuiltInImageCreateView) "
                        "without the 'target_model' attribute is prohibited.")
        self.assertIn(expected_msg, cm.exception.args[0])

    def test_cbv_disable_server_side_crop(self):
        file = find("demo/screen_upload.png")

        with open(file, "rb") as fp:
            data = {"files[]": fp}
            request = self.factory.post(
                self.get_demo_upload_url(), data=data,
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        resp = built_in_views.BuiltInImageCreateView.as_view(
            disable_server_side_crop=True)(request)

        self.assertEqual(resp.status_code, 200, resp.content)

    def test_cbv_invalid_crop_url(self):
        file = find("demo/screen_upload.png")

        with open(file, "rb") as fp:
            data = {"files[]": fp}
            request = self.factory.post(
                self.get_demo_upload_url(), data=data,
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        with self.assertRaises(ImproperlyConfigured) as cm:
            built_in_views.BuiltInImageCreateView.as_view(
                crop_url_name="invalid-crop-url")(request)

        expected_msg = ("'crop_url_name' in BuiltInImageCreateView "
                        "is invalid. The exception is: NoReverseMatch: "
                        "Reverse for 'invalid-crop-url' not found.")

        self.assertIn(expected_msg, cm.exception.args[0])

    def test_cbv_crop_url_not_configured(self):
        file = find("demo/screen_upload.png")

        with open(file, "rb") as fp:
            data = {"files[]": fp}
            request = self.factory.post(
                self.get_demo_upload_url(), data=data,
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        resp = built_in_views.BuiltInImageCreateView.as_view(
            crop_url_name=None)(request)

        self.assertEqual(resp.status_code, 200, resp.content)

    def test_cbv_crop_url_conflict(self):
        # target_model not built-in while crop url name is
        # using built-in crop url name
        file = find("demo/screen_upload.png")

        with open(file, "rb") as fp:
            data = {"files[]": fp}
            request = self.factory.post(
                self.get_demo_upload_url(), data=data,
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        with self.assertRaises(ImproperlyConfigured) as cm:
            built_in_views.BuiltInImageCreateView.as_view(
                target_model="tests.FakeValidImageModel")(request)

        expected_msg = ("'crop_url_name' in BuiltInImageCreateView "
                        "is using built-in default, while 'target_model' "
                        "is not using built-in default value")
        self.assertIn(expected_msg, cm.exception.args[0])

    def test_cbv_thumbnail_size_invalid(self):
        file = find("demo/screen_upload.png")

        data = {"thumbnail_size": "100.1"}

        with open(file, "rb") as fp:
            data["files[]"] = fp
            request = self.factory.post(
                self.get_demo_upload_url(), data=data,
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        with self.assertRaises(ImproperlyConfigured) as cm:
            built_in_views.BuiltInImageCreateView.as_view()(request)

        expected_msg = ("'thumbnail_size' must be an int, or a string of int, "
                        "or a string in the form of '80x60', or a list or tuple of "
                        "2 ints, e.g, [80, 60] or (80, 60).")

        self.assertIn(expected_msg, cm.exception.args[0])


@override_settings(MEDIA_ROOT=test_media_root)
class GalleryWidgetFetchViewTest(ViewTestMixin, TestCase):

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
            resp = self.c.get(self.get_demo_fetch_url(
                params={"pks": list(gallery.images)}),
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(resp.status_code, 200)
            resp_image_list = [
                file["pk"] for file in json.loads(resp.content)["files"]]
            return resp_image_list

        image_list = list(gallery.images)

        self.c.force_login(self.user)
        self.assertEqual(image_list, get_fetched_result())

        self.c.force_login(self.superuser)
        self.assertEqual(image_list, get_fetched_result())

        another_user = self.create_user()
        self.c.force_login(another_user)
        self.assertEqual(len(get_fetched_result()), 0)

    def test_fetch_thumbnail_size_list(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=2,
            shuffle=True)

        self.c.force_login(self.user)

        url = self.get_demo_fetch_url(
            params={"pks": list(gallery.images)})

        url += "&thumbnail_size=100&thumbnail_size=150"

        resp = self.c.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200)

    def test_fetch_without_pks(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        self.c.force_login(self.user)
        resp = self.c.get(self.get_demo_fetch_url(
            params={"not-pks": list(gallery.images)}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resp.status_code, 400)

    def test_fetch_fail_not_xml(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        self.c.force_login(self.user)
        resp = self.c.get(self.get_demo_fetch_url(
            params={"not-pks": list(gallery.images)})
        )

        # notice: not 400
        self.assertEqual(resp.status_code, 403)

    def test_fetch_pk_not_digit(self):
        self.c.force_login(self.user)
        resp = self.c.get(self.get_demo_fetch_url(
            params={"pks": [1.1]}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resp.status_code, 400)

    def test_fetch_pk_decode_error(self):
        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        self.c.force_login(self.user)
        resp = self.c.get(self.get_demo_fetch_url(
            params={"pks": "abcd"}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resp.status_code, 400)

    def test_fetch_pk_loaded_but_not_list(self):
        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        self.c.force_login(self.user)
        resp = self.c.get(self.get_demo_fetch_url(
            params={"pks": '{"ab": "cd"}'}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resp.status_code, 400)

    def test_fetch_not_logged_in(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        resp = self.c.get(self.get_demo_fetch_url(
            params={"not-pks": list(gallery.images)}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(resp.status_code, 302)

    def test_cbv_target_model_not_configured(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=2,
            shuffle=True)

        request = self.factory.get(
            self.get_demo_fetch_url(
                params={"pks": list(gallery.images)}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        with self.assertRaises(ImproperlyConfigured) as cm:
            built_in_views.BuiltInImageListView.as_view(
                target_model=None)(request)

        expected_msg = ("Using BaseImageModelMixin (base class of "
                        "BuiltInImageListView) "
                        "without the 'target_model' attribute is prohibited.")
        self.assertIn(expected_msg, cm.exception.args[0])

    def test_cbv_disable_server_side_crop(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=2,
            shuffle=True)

        request = self.factory.get(
            self.get_demo_fetch_url(
                params={"pks": list(gallery.images)}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        resp = built_in_views.BuiltInImageListView.as_view(
            disable_server_side_crop=True)(request)
        self.assertEqual(resp.status_code, 200)

    def test_cbv_invalid_crop_url(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=2,
            shuffle=True)

        request = self.factory.get(
            self.get_demo_fetch_url(
                params={"pks": list(gallery.images)}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        with self.assertRaises(ImproperlyConfigured) as cm:
            built_in_views.BuiltInImageListView.as_view(
                crop_url_name="invalid-crop-url")(request)

        expected_msg = ("'crop_url_name' in BuiltInImageListView "
                        "is invalid. The exception is: NoReverseMatch: "
                        "Reverse for 'invalid-crop-url' not found.")

        self.assertIn(expected_msg, cm.exception.args[0])

    def test_cbv_crop_url_not_configured(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=2,
            shuffle=True)

        request = self.factory.get(
            self.get_demo_fetch_url(
                params={"pks": list(gallery.images)}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        resp = built_in_views.BuiltInImageListView.as_view(
            crop_url_name=None)(request)

        self.assertEqual(resp.status_code, 200)

    def test_cbv_crop_url_conflict(self):
        # target_model not built-in while crop URL name is
        # using crop url name of built-in image model
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=2,
            shuffle=True)

        request = self.factory.get(
            self.get_demo_fetch_url(
                params={"pks": list(gallery.images)}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        with self.assertRaises(ImproperlyConfigured) as cm:
            built_in_views.BuiltInImageListView.as_view(
                target_model="tests.FakeValidImageModel")(request)

        expected_msg = ("'crop_url_name' in BuiltInImageListView "
                        "is using built-in default, while 'target_model' "
                        "is not using built-in default value")
        self.assertIn(expected_msg, cm.exception.args[0])

    def test_cbv_thumbnail_size_invalid(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=2,
            shuffle=True)

        request = self.factory.get(
            self.get_demo_fetch_url(
                params={"pks": list(gallery.images),
                        "thumbnail_size": 100.1}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        with self.assertRaises(ImproperlyConfigured) as cm:
            built_in_views.BuiltInImageListView.as_view()(request)

        expected_msg = ("'thumbnail_size' must be an int, or a string of int, "
                        "or a string in the form of '80x60', or a list of2 ints, "
                        "e.g, [80, 60]. "
                        "Ref: https://stackoverflow.com/a/30107874/3437454")

        self.assertIn(expected_msg, cm.exception.args[0])

    def test_cbv_image_unexpectedly_deleted(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=2,
            shuffle=True)

        from sorl.thumbnail import delete

        for obj in BuiltInGalleryImage.objects.all():
            # Why this won't delete the thumbnail cache?
            delete(obj.image.path, delete_file=True)

        request = self.factory.get(
            self.get_demo_fetch_url(
                params={"pks": list(gallery.images)}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        resp = built_in_views.BuiltInImageListView.as_view()(request)

        self.assertEqual(resp.status_code, 200)

        resp_files = json.loads(resp.content)['files']
        for f in resp_files:
            self.assertEqual(f['error'],
                             'image: The image was unexpectedly deleted from server')

    def test_cbv_get_thumbnail_error(self):
        gallery = factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=5,
            shuffle=True)

        factories.DemoGalleryFactory.create(
            creator=self.user, number_of_images=2,
            shuffle=True)

        request = self.factory.get(
            self.get_demo_fetch_url(
                params={"pks": list(gallery.images)}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        with mock.patch("galleryfield.mixins.get_thumbnail") as mock_get_thumb:
            mock_get_thumb.side_effect = RuntimeError("Unexpected error")
            resp = built_in_views.BuiltInImageListView.as_view()(request)

        self.assertEqual(resp.status_code, 200)

        resp_files = json.loads(resp.content)['files']
        for f in resp_files:
            self.assertEqual(f['error'],
                             'thumbnail: RuntimeError: Unexpected error')


@override_settings(MEDIA_ROOT=test_media_root)
class GalleryWidgetCropViewTest(ViewTestMixin, TestCase):

    def get_crop_post_data(self, **kwargs):
        default_result = {
            "x": 200, "y": 200, "width": 400,
            "height": 810, "rotate": -90}
        default_result.update(**kwargs)
        cropped = self.get_cropped_result(**default_result)
        data = self._get_crop_post_data(cropped_result=cropped)
        return data

    def test_crop_success(self):
        pk = self.get_demo_crop_pk(0)
        data = self.get_default_crop_post_data()

        self.c.force_login(self.user)
        resp = self.c.post(
            self.get_demo_crop_url(pk), data=data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200)

        pk = self.get_demo_crop_pk(1)
        data = self.get_default_crop_post_data()
        self.c.force_login(self.superuser)
        resp = self.c.post(
            self.get_demo_crop_url(pk), data=data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200)

    def test_crop_fail_not_xml(self):
        pk = self.get_demo_crop_pk(0)
        data = self.get_default_crop_post_data()

        self.c.force_login(self.user)
        resp = self.c.post(
            self.get_demo_crop_url(pk), data=data)
        self.assertEqual(resp.status_code, 403)

    def test_crop_png(self):
        self.demo_upload_file(self.user, find("demo/screen_upload.png"))
        factories.DemoGalleryFactory.create(
            creator=self.user, images=[BuiltInGalleryImage.objects.first()])
        data = self.get_crop_post_data()

        self.c.force_login(self.user)
        resp = self.c.post(self.get_demo_crop_url(1), data=data,
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200)

    def test_crop_non_exist_image(self):
        data = self.get_crop_post_data()

        self.c.force_login(self.user)
        resp = self.c.post(self.get_demo_crop_url(100), data=data,
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 404)

    def test_crop_cropResult_invalid(self):
        data = self.get_default_crop_post_data(x=None)

        self.c.force_login(self.user)
        pk = self.get_demo_crop_pk(1)
        resp = self.c.post(self.get_demo_crop_url(pk), data=data,
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 400)

    def test_crop_no_cropResult(self):
        data = self.get_default_crop_post_data(x=None)

        data.pop("cropped_result")

        self.c.force_login(self.user)
        pk = self.get_demo_crop_pk(1)
        resp = self.c.post(self.get_demo_crop_url(pk), data=data,
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 400)

    def test_crop_cropResult_not_json(self):
        data = self.get_default_crop_post_data(x=None)

        data["cropped_result"] = {
            "x": 100, "y": 200, "width": 400, "height": 810, "rotate": -90}

        self.c.force_login(self.user)
        pk = self.get_demo_crop_pk(1)
        resp = self.c.post(self.get_demo_crop_url(pk), data=data,
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 400)

    def test_crop_no_rotate(self):
        data = self.get_default_crop_post_data(rotate=0)

        pk = self.get_demo_crop_pk(1)
        self.c.force_login(self.user)
        resp = self.c.post(self.get_demo_crop_url(pk), data=data,
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200, resp.content)

    def test_crop_io_error(self):
        # no actual image file
        gallery = factories.DemoGalleryFactory.create(creator=self.user)
        os.remove(gallery.images.objects.first().image.path)

        pk = gallery.images.objects.first().pk
        data = self.get_crop_post_data()
        self.c.force_login(self.user)
        resp = self.c.post(self.get_demo_crop_url(pk), data=data,
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 400)

    def test_crop_permission_denied(self):
        pk = self.get_demo_crop_pk(0)
        data = self.get_default_crop_post_data()

        another_user = self.create_user()
        self.c.force_login(another_user)
        resp = self.c.post(self.get_demo_crop_url(pk), data=data,
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 403)

    def test_crop_not_logged_in(self):
        pk = self.get_demo_crop_pk(0)
        data = self.get_default_crop_post_data()

        resp = self.c.post(self.get_demo_crop_url(pk), data=data,
                           HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 302)

    def test_cbv_target_model_not_configured(self):
        pk = self.get_demo_crop_pk(0)
        data = self.get_default_crop_post_data()

        request = self.factory.post(
            self.get_demo_crop_url(pk), data=data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        kwargs = {"pk": pk}

        with self.assertRaises(ImproperlyConfigured) as cm:
            built_in_views.BuiltInImageCropView.as_view(
                target_model=None)(request, **kwargs)

        expected_msg = ("Using BaseImageModelMixin (base class of "
                        "BuiltInImageCropView) "
                        "without the 'target_model' attribute is prohibited.")
        self.assertIn(expected_msg, cm.exception.args[0])

    def test_cbv_disable_server_side_crop(self):
        pk = self.get_demo_crop_pk(0)
        data = self.get_default_crop_post_data()

        request = self.factory.post(
            self.get_demo_crop_url(pk), data=data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        kwargs = {"pk": pk}

        with self.assertRaises(SuspiciousOperation) as cm:
            resp = built_in_views.BuiltInImageCropView.as_view(
                disable_server_side_crop=True)(request, **kwargs)
            self.assertEqual(resp.status_code, 400)

        expected_msg = "Server side crop is not enabled"
        self.assertIn(expected_msg, cm.exception.args[0])

    def test_cbv_invalid_crop_url(self):
        pk = self.get_demo_crop_pk(0)
        data = self.get_default_crop_post_data()

        request = self.factory.post(
            self.get_demo_crop_url(pk), data=data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        kwargs = {"pk": pk}

        with self.assertRaises(ImproperlyConfigured) as cm:
            built_in_views.BuiltInImageCropView.as_view(
                crop_url_name="invalid-crop-url")(request, **kwargs)

        expected_msg = ("'crop_url_name' in BuiltInImageCropView "
                        "is invalid. The exception is: NoReverseMatch: "
                        "Reverse for 'invalid-crop-url' not found.")

        self.assertIn(expected_msg, cm.exception.args[0])

    def test_cbv_crop_url_not_configured(self):
        pk = self.get_demo_crop_pk(0)
        data = self.get_default_crop_post_data()

        kwargs = {"pk": pk}
        request = self.factory.post(
            self.get_demo_crop_url(pk), data=data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        resp = built_in_views.BuiltInImageCropView.as_view(
            crop_url_name=None)(request, **kwargs)

        self.assertEqual(resp.status_code, 200)

    def test_cbv_crop_url_conflict(self):
        # target_model not built-in while crop url name is
        # using built-in crop url name
        pk = self.get_demo_crop_pk(0)
        data = self.get_default_crop_post_data()

        kwargs = {"pk": pk}
        request = self.factory.post(
            self.get_demo_crop_url(pk), data=data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        with self.assertRaises(ImproperlyConfigured) as cm:
            built_in_views.BuiltInImageCropView.as_view(
                target_model="tests.FakeValidImageModel")(request, **kwargs)

        expected_msg = ("'crop_url_name' in BuiltInImageCropView "
                        "is using built-in default, while 'target_model' "
                        "is not using built-in default value")
        self.assertIn(expected_msg, cm.exception.args[0])

    def test_cbv_thumbnail_size_invalid(self):
        pk = self.get_demo_crop_pk(0)
        data = self.get_default_crop_post_data()
        data["thumbnail_size"] = 100.1

        kwargs = {"pk": pk}
        request = self.factory.post(
            self.get_demo_crop_url(pk), data=data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user

        with self.assertRaises(ImproperlyConfigured) as cm:
            built_in_views.BuiltInImageCropView.as_view()(request, **kwargs)

        expected_msg = ("'thumbnail_size' must be an int, or a string of int, "
                        "or a string in the form of '80x60', or a list or tuple of "
                        "2 ints, e.g, [80, 60] or (80, 60).")

        self.assertIn(expected_msg, cm.exception.args[0])
