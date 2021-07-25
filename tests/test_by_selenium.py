import os.path
import json
from time import sleep
from urllib.parse import urljoin

from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.test.utils import override_settings
from selenium import webdriver
import tempfile

from tests.utils import remove_upload_directory
from tests.mixins import UserCreateMixin
from gallery.models import BuiltInGalleryImage
from demo.models import DemoGallery


CHROMIUM = "chromium"
FIREFOX = "firefox"
SELENIUM_BROWSER = CHROMIUM


test_media_root = os.path.join(tempfile.gettempdir(), "gallery_widget_media")


@override_settings(MEDIA_ROOT=test_media_root)
class TestAdminPanelWidget(UserCreateMixin, StaticLiveServerTestCase):
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
        return self.get_full_url(reverse("gallery"))

    def _login_to_admin(self):
        # We do this because we need to login
        self.selenium.get(self.admin_url)
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(self.superuser.username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys("secret")
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()
        sleep(1)

    def _go_to_new_gallery(self):
        self.selenium.get(self.new_gallery_url)

    def _assert_widget_loaded(self):
        sleep(1)
        self.selenium.find_element_by_id("images-files")

    def _add_and_upload_image(self, static_file_path):
        input_ele = self.selenium.find_element_by_id("images-files")
        input_ele.send_keys(self._get_upload_image(static_file_path))
        sleep(0.5)
        self.selenium.find_element_by_class_name("start").click()
        sleep(1)

    def _get_upload_image(self, static_file_path):
        return find(static_file_path)

    def _submit_page(self):
        submit_ele = self.selenium.find_element_by_id("submit-id-submit")
        submit_ele.click()
        sleep(0.5)

    def _get_first_button_bar_delete_button(self):
        return self.selenium.find_element_by_css_selector("a.delete.fileinput-button")

    def _delete_one_image(self):
        delete_button = self._get_first_button_bar_delete_button()
        delete_button.click()
        sleep(0.5)

    @staticmethod
    def _get_number_of_images(instance):
        image_info_list = json.loads(instance.images)
        return len(image_info_list)

    def test_upload_image(self):
        self.assertEqual(DemoGallery.objects.count(), 0)
        self._login_to_admin()
        self._go_to_new_gallery()
        self._assert_widget_loaded()
        self._add_and_upload_image("demo/screen1.png")
        self.assertEqual(BuiltInGalleryImage.objects.count(), 1)
        self._submit_page()
        self._add_and_upload_image("demo/screen2.png")
        self.assertEqual(BuiltInGalleryImage.objects.count(), 2)
        self._submit_page()
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(self._get_number_of_images(DemoGallery.objects.first()), 2)

    def test_delete_image(self):
        self.assertEqual(DemoGallery.objects.count(), 0)
        self._login_to_admin()
        self._go_to_new_gallery()
        self._assert_widget_loaded()
        self._add_and_upload_image("demo/screen1.png")
        self._add_and_upload_image("demo/screen2.png")

        self._delete_one_image()
        self._submit_page()
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(self._get_number_of_images(DemoGallery.objects.first()), 1)

        self._delete_one_image()
        self._submit_page()
        self.assertEqual(DemoGallery.objects.count(), 1)
        # Because this is the last image, delete is not allowed
        # because this field is required
        self.assertEqual(self._get_number_of_images(DemoGallery.objects.first()), 1)
