from time import sleep
from urllib.parse import urljoin

from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test.utils import override_settings
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By

from demo.models import DemoGallery
from demo_custom.models import CustomDemoGallery, CustomImage
from galleryfield.models import BuiltInGalleryImage
from tests.mixins import UserCreateMixin
from tests.utils import remove_upload_directory, test_media_root

CHROMIUM = "chromium"
FIREFOX = "firefox"
SELENIUM_BROWSER = CHROMIUM


class SeleniumTestMixin(UserCreateMixin):

    @property
    def gallery_create_url_name(self):
        raise NotImplementedError

    @property
    def gallery_detail_url_name(self):
        raise NotImplementedError

    @property
    def image_model(self):
        raise NotImplementedError

    @property
    def gallery_model(self):
        raise NotImplementedError

    @classmethod
    def setUpClass(cls):
        if SELENIUM_BROWSER == CHROMIUM:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            cls.selenium = webdriver.Chrome(options=options)
        elif SELENIUM_BROWSER == FIREFOX:
            cls.selenium = webdriver.Firefox()
        super().setUpClass()

    def setUp(self):
        super().setUp()
        remove_upload_directory()
        self.superuser = self.create_superuser()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def get_full_url(self, url):
        return urljoin(self.live_server_url, url)

    @property
    def admin_url(self):
        return self.get_full_url("/admin/")

    @property
    def new_gallery_url(self):
        return self.get_full_url(reverse(self.gallery_create_url_name))

    def get_gallery_detail_url(self, pk):
        return self.get_full_url(reverse(
            self.gallery_detail_url_name, kwargs={"pk": pk}))

    def _login_to_admin(self):
        # We do this because we need to login
        self.selenium.get(self.admin_url)
        username_input = self.selenium.find_element(by=By.NAME, value="username")
        username_input.send_keys(self.superuser.username)
        password_input = self.selenium.find_element(by=By.NAME, value="password")
        password_input.send_keys("secret")
        self.selenium.find_element(
            by=By.XPATH, value='//input[@value="Log in"]').click()
        sleep(1)

    def _go_to_new_gallery(self):
        self.selenium.get(self.new_gallery_url)

    def _go_to_gallery_detail(self, pk):
        self.selenium.get(self.get_gallery_detail_url(pk))
        sleep(1)

    def _assert_widget_loaded(self):
        sleep(1)
        self.selenium.find_element(by=By.ID, value="images-files")

    def _add_and_upload_image(self, static_file_path):
        input_ele = self.selenium.find_element(by=By.ID, value="images-files")
        input_ele.send_keys(self._get_upload_image(static_file_path))
        sleep(0.5)
        self.selenium.find_element(by=By.CLASS_NAME, value="start").click()
        sleep(1)

    def _get_upload_image(self, static_file_path):
        return find(static_file_path)

    def _submit_page(self):
        submit_ele = self.selenium.find_element(by=By.ID, value="submit-id-submit")
        submit_ele.click()
        sleep(0.5)

    def _get_first_button_bar_delete_button(self):
        return self.selenium.find_element(by=By.CSS_SELECTOR,
                                          value="a.delete.fileinput-button")

    def _delete_one_image(self):
        delete_button = self._get_first_button_bar_delete_button()
        delete_button.click()
        sleep(0.5)

    def test_upload_image(self):
        self.assertEqual(self.gallery_model.objects.count(), 0)
        self._login_to_admin()
        self._go_to_new_gallery()
        self._assert_widget_loaded()
        self._add_and_upload_image("demo/screen_upload.png")
        self.assertEqual(self.image_model.objects.count(), 1)
        self._submit_page()
        self._add_and_upload_image("demo/screen_crop.png")
        self.assertEqual(self.image_model.objects.count(), 2)
        self._submit_page()
        self.assertEqual(self.gallery_model.objects.count(), 1)
        self.assertEqual(
            self.gallery_model.objects.first().images.objects.count(), 2)
        self._go_to_gallery_detail(self.gallery_model.objects.first().pk)

    def test_delete_image(self):
        self.assertEqual(self.gallery_model.objects.count(), 0)
        self._login_to_admin()
        self._go_to_new_gallery()
        self._assert_widget_loaded()
        self._add_and_upload_image("demo/screen_upload.png")
        self._add_and_upload_image("demo/screen_crop.png")

        self._delete_one_image()
        self._submit_page()
        self.assertEqual(self.gallery_model.objects.count(), 1)
        self.assertEqual(
            self.gallery_model.objects.first().images.objects.count(), 1)

        self._delete_one_image()
        self._submit_page()
        self.assertEqual(self.gallery_model.objects.count(), 1)
        # Because this is the last image, delete is not allowed
        # because this field is required
        self.assertEqual(
            self.gallery_model.objects.first().images.objects.count(), 1)

    def test_delete_one_before_saving(self):
        self.assertEqual(self.gallery_model.objects.count(), 0)
        self._login_to_admin()
        self._go_to_new_gallery()
        self._assert_widget_loaded()
        self._add_and_upload_image("demo/screen_upload.png")
        self._add_and_upload_image("demo/screen_crop.png")

        # Delete the first uploaded image
        self.assertEqual(self.image_model.objects.count(), 2)
        self.image_model.objects.first().delete()
        self.assertEqual(self.image_model.objects.count(), 1)

        self._submit_page()
        self.assertEqual(self.gallery_model.objects.count(), 1)
        self.assertEqual(
            self.gallery_model.objects.first().images.objects.count(), 1)


@override_settings(MEDIA_ROOT=test_media_root)
class TestDemoApp(SeleniumTestMixin, StaticLiveServerTestCase):

    gallery_create_url_name = "gallery"

    gallery_detail_url_name = "gallery-detail"

    image_model = BuiltInGalleryImage

    gallery_model = DemoGallery


@override_settings(MEDIA_ROOT=test_media_root)
class TestCustomDemoApp(SeleniumTestMixin, StaticLiveServerTestCase):

    gallery_create_url_name = "custom-gallery"

    gallery_detail_url_name = "custom-gallery-detail"

    image_model = CustomImage

    gallery_model = CustomDemoGallery
