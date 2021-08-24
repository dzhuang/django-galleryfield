from time import sleep
from urllib.parse import urljoin

from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test.utils import override_settings
from django.urls import reverse
from selenium import webdriver

from demo.models import DemoGallery
from galleryfield.models import BuiltInGalleryImage
from tests.mixins import UserCreateMixin
from tests.utils import remove_upload_directory, test_media_root

CHROMIUM = "chromium"
FIREFOX = "firefox"
SELENIUM_BROWSER = CHROMIUM


@override_settings(MEDIA_ROOT=test_media_root)
class TestWidgetBySelenium(UserCreateMixin, StaticLiveServerTestCase):
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

    def get_gallery_detail_url(self, pk):
        return self.get_full_url(reverse("gallery-detail", kwargs={"pk": pk}))

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

    def _go_to_gallery_detail(self, pk):
        self.selenium.get(self.get_gallery_detail_url(pk))
        sleep(1)

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

    def test_upload_image(self):
        self.assertEqual(DemoGallery.objects.count(), 0)
        self._login_to_admin()
        self._go_to_new_gallery()
        self._assert_widget_loaded()
        self._add_and_upload_image("demo/screen_upload.png")
        self.assertEqual(BuiltInGalleryImage.objects.count(), 1)
        self._submit_page()
        self._add_and_upload_image("demo/screen_crop.png")
        self.assertEqual(BuiltInGalleryImage.objects.count(), 2)
        self._submit_page()
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(DemoGallery.objects.first().images.objects.count(), 2)
        self._go_to_gallery_detail(DemoGallery.objects.first().pk)

    def test_delete_image(self):
        self.assertEqual(DemoGallery.objects.count(), 0)
        self._login_to_admin()
        self._go_to_new_gallery()
        self._assert_widget_loaded()
        self._add_and_upload_image("demo/screen_upload.png")
        self._add_and_upload_image("demo/screen_crop.png")

        self._delete_one_image()
        self._submit_page()
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(DemoGallery.objects.first().images.objects.count(), 1)

        self._delete_one_image()
        self._submit_page()
        self.assertEqual(DemoGallery.objects.count(), 1)
        # Because this is the last image, delete is not allowed
        # because this field is required
        self.assertEqual(DemoGallery.objects.first().images.objects.count(), 1)

    def test_delete_one_before_saving(self):
        self.assertEqual(DemoGallery.objects.count(), 0)
        self._login_to_admin()
        self._go_to_new_gallery()
        self._assert_widget_loaded()
        self._add_and_upload_image("demo/screen_upload.png")
        self._add_and_upload_image("demo/screen_crop.png")

        # Delete the first uploaded image
        self.assertEqual(BuiltInGalleryImage.objects.count(), 2)
        BuiltInGalleryImage.objects.first().delete()
        self.assertEqual(BuiltInGalleryImage.objects.count(), 1)

        self._submit_page()
        self.assertEqual(DemoGallery.objects.count(), 1)
        self.assertEqual(DemoGallery.objects.first().images.objects.count(), 1)
