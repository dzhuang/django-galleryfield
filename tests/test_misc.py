from django.urls import reverse, NoReverseMatch
from django.test import SimpleTestCase
from django.core.exceptions import ImproperlyConfigured


from gallery.utils import get_url_from_str


class GetUrlFromStrTest(SimpleTestCase):
    # Test gallery.utils.get_url_from_str

    def test_None(self):
        self.assertIsNone(get_url_from_str(None))
        self.assertIsNone(get_url_from_str(""))

    def test_valid_url_name(self):
        self.assertEqual(
            get_url_from_str("gallery_image_upload"),
            reverse("gallery_image_upload")
        )

    def test_invalid_url_name(self):
        with self.assertRaises(NoReverseMatch):
            # We are evaluating the lazy_result when compare
            self.assertEqual(get_url_from_str("non-exist-url-name"), "")
        with self.assertRaises(ImproperlyConfigured) as cm:
            get_url_from_str("non-exist-url-name", require_urlconf_ready=True)
        self.assertIn("is neither a valid url nor a valid url name",
                      cm.exception.args[0])

    def test_valid_url(self):
        url = reverse("gallery-update", kwargs={"pk": 1})
        self.assertEqual(
            get_url_from_str(url),
            url
        )

    def test_invalid_url(self):
        with self.assertRaises(NoReverseMatch):
            # We are evaluating the lazy_result when compare
            self.assertEqual(get_url_from_str("/foo/bar"), "")
        with self.assertRaises(ImproperlyConfigured) as cm:
            get_url_from_str("/foo/bar", require_urlconf_ready=True)
        self.assertIn("is neither a valid url nor a valid url name",
                      cm.exception.args[0])