from django.test import SimpleTestCase
from django.test.utils import override_settings


class CheckSettingsBase(SimpleTestCase):
    @property
    def func(self):
        from gallery.checks import check_settings
        return check_settings

    @property
    def msg_id_prefix(self):
        raise NotImplementedError()

    def assertCheckMessages(self,  # noqa
                            expected_ids=None, expected_msgs=None, length=None,
                            filter_message_id_prefixes=None, ignore_order=False):
        """
        Check the run check result of the setting item of the testcase instance
        :param expected_ids: Optional, list of expected message id,
        default to None
        :param expected_msgs: Optional, list of expected message string,
        default to None
        :param length: Optional, length of expected check message,
        default to None
        :param filter_message_id_prefixes: a list or tuple of message id prefix,
        to restrict the
         run check result to be within the iterable.
        """
        if not filter_message_id_prefixes:
            filter_message_id_prefixes = self.msg_id_prefix
            if isinstance(filter_message_id_prefixes, str):
                filter_message_id_prefixes = [filter_message_id_prefixes]
            assert isinstance(filter_message_id_prefixes, (list, tuple))

        if expected_ids is None and expected_msgs is None and length is None:
            raise RuntimeError("At least one parameter should be specified "
                               "to make the assertion")

        result = self.func(None)

        def is_id_in_filter(id, filter):
            prefix = id.split(".")[0]
            return prefix in filter

        try:
            result_ids, result_msgs = (
                list(zip(*[(r.id, r.msg) for r in result
                      if is_id_in_filter(r.id, filter_message_id_prefixes)])))

            if expected_ids is not None:
                assert isinstance(expected_ids, (list, tuple))
                if ignore_order:
                    result_ids = tuple(sorted(list(result_ids)))
                    expected_ids = sorted(list(expected_ids))
                self.assertEqual(result_ids, tuple(expected_ids))

            if expected_msgs is not None:
                assert isinstance(expected_msgs, (list, tuple))
                if ignore_order:
                    result_msgs = tuple(sorted(list(result_msgs)))
                    expected_msgs = sorted(list(expected_msgs))
                self.assertEqual(result_msgs, tuple(expected_msgs))

            if length is not None:
                self.assertEqual(len(expected_ids), len(result_ids))
        except ValueError as e:
            if "values to unpack" in str(e):
                if expected_ids or expected_msgs or length:
                    self.fail("Check message unexpectedly found to be empty")
            else:
                raise


class CheckConfigs(CheckSettingsBase):
    msg_id_prefix = "django-gallery-widget"
    VALID_CONF_None = None
    VALID_CONF_Dict = {}
    INVALID_CONF_EMPTY_LIST = []
    INVALID_CONF_SPACES = " "

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF_None)
    def test_valid_config1(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF_Dict)
    def test_valid_config2(self):
        self.assertCheckMessages([])

    @override_settings(INSTALLED_APPS=['gallery', 'demo'])
    def test_invalid_config1(self):
        self.assertCheckMessages(["django-gallery-widget.E001"])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=INVALID_CONF_EMPTY_LIST)
    def test_invalid_config2(self):
        self.assertCheckMessages(["django-gallery-widget.E002"])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=INVALID_CONF_SPACES)
    def test_invalid_config3(self):
        self.assertCheckMessages(["django-gallery-widget.E002"])


"""
DJANGO_GALLERY_WIDGET_CONFIG = {
    "assets": {
        "bootstrap_js_path": 'vendor/bootstrap/dist/js/bootstrap.min.js',
        "bootstrap_css_path": "vendor/bootstrap/dist/css/bootstrap.min.css",
        "jquery_js_path": "vendor/jquery.min.js",
        "extra_js": [],
        "extra_css": [],
    },
    "thumbnails": {
        "size": 120,
        "quality": 80
    },
    "widget_hidden_input_css_class": "django-gallery-widget",
    "prompt_alert_if_changed_on_window_reload": True,
}
"""


class CheckAssets(CheckSettingsBase):
    msg_id_prefix = "django-gallery-widget-assets"

    VALID_CONF_None = {"assets": None}

    VALID_CONF_Dict = {"assets": dict()}

    VALID_CONF = {
        "assets": {
            "jquery.js": "jquery/dist/jquery.min.js",
            "bootstrap.css": "bootstrap/dist/css/bootstrap.min.css",
            "extra_js": ["some/js"],
            "extra_css": ["some/css"],
        },
    }

    VALID_CONF_EXTRA_None = {
        "assets": {
            "extra_js": None,
            "extra_css": None,
        },
    }

    CONF_SET_NONE_WARNED = {
        "assets": {
            "jquery.js": None,
        },
    }

    INVALID_CONF_NOT_Dict = {
        "assets": object
    }

    NOT_LISTED_ASSET = {
        "assets": {
            "bootstrap4.css": "bootstrap/dist/css/bootstrap.min.css",
        },
    }

    INVALID_CONF_EXTRA_JS = {
        "assets": {
            "extra_js": "extra_js",
        },
    }

    INVALID_CONF_EXTRA_JS_ELE = {
        "assets": {
            "extra_js": ["extra_js", object, 1],
        },
    }

    INVALID_CONF_EXTRA_CSS = {
        "assets": {
            "extra_css": "extra_css",
        },
    }

    INVALID_CONF_EXTRA_CSS_ELE = {
        "assets": {
            "extra_css": ["extra_css", object, 2]
        },
    }

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF_None)
    def test_valid_config1(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF_Dict)
    def test_valid_config2(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF)
    def test_valid_config3(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF_EXTRA_None)
    def test_valid_config4(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=NOT_LISTED_ASSET)
    def test_item_not_listed_warned_config(self):
        self.assertCheckMessages(["django-gallery-widget-assets.W001"])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=CONF_SET_NONE_WARNED)
    def test_item_set_none_warned_config(self):
        self.assertCheckMessages(["django-gallery-widget-assets.W002"])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=INVALID_CONF_NOT_Dict)
    def test_invalid_config01(self):
        self.assertCheckMessages(["django-gallery-widget-assets.E001"])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=INVALID_CONF_EXTRA_JS)
    def test_invalid_config02(self):
        self.assertCheckMessages(["django-gallery-widget-assets.E005"])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=INVALID_CONF_EXTRA_CSS)
    def test_invalid_config03(self):
        self.assertCheckMessages(["django-gallery-widget-assets.E007"])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=INVALID_CONF_EXTRA_JS_ELE)
    def test_invalid_config04(self):
        self.assertCheckMessages(["django-gallery-widget-assets.E006",
                                  "django-gallery-widget-assets.E006"])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=INVALID_CONF_EXTRA_CSS_ELE)
    def test_invalid_config05(self):
        self.assertCheckMessages(["django-gallery-widget-assets.E008",
                                  "django-gallery-widget-assets.E008"])


"""
    "thumbnails": {
        "size": 120,
        "quality": 80
    },
"""


class CheckThumbnails(CheckSettingsBase):
    msg_id_prefix = "django-gallery-widget-thumbnails"

    VALID_CONF_None = {"thumbnails": None}

    VALID_CONF_Dict = {"thumbnails": dict()}

    VALID_CONF = {
        "thumbnails": {
            "size": 150,
            "quality": 95
        },
    }

    VALID_CONF_ALL_None = {
        "thumbnails": {
            "size": None,
            "quality": None
        },
    }

    VALID_CONF_CAN_CONVERT_TO_NUMBER = {
        "thumbnails": {
            "size": None,
            "quality": None
        },
    }

    INVALID_CONF_NOT_Dict = {
        "thumbnails": object
    }

    INVALID_CONF_NOT_NUMBER = {
        "thumbnails": {
            "size": "one hundred",
            "quality": "ninety"
        },
    }

    INVALID_CONF_NEGATIVE = {
        "thumbnails": {
            "size": -10,
            "quality": -0.1
        },
    }

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF_None)
    def test_valid_config1(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF_Dict)
    def test_valid_config2(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF)
    def test_valid_config3(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF_ALL_None)
    def test_valid_config4(self):
        self.assertCheckMessages([])

    @override_settings(
        DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF_CAN_CONVERT_TO_NUMBER)
    def test_valid_config5(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=INVALID_CONF_NOT_Dict)
    def test_invalid_config1(self):
        self.assertCheckMessages(["django-gallery-widget-thumbnails.E001"])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=INVALID_CONF_NOT_NUMBER)
    def test_invalid_config2(self):
        self.assertCheckMessages([
            "django-gallery-widget-thumbnails.E002",
            "django-gallery-widget-thumbnails.E004"])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=INVALID_CONF_NEGATIVE)
    def test_invalid_config3(self):
        self.assertCheckMessages([
            "django-gallery-widget-thumbnails.E003",
            "django-gallery-widget-thumbnails.E005"])


"""
    "widget_hidden_input_css_class": "django-gallery-widget",
"""


class CheckMultifieldCssClassBasename(CheckSettingsBase):
    msg_id_prefix = "django-gallery-widget-widget_hidden_input_css_class"

    VALID_CONF_None = {"widget_hidden_input_css_class": None}

    VALID_CONF_str = {"widget_hidden_input_css_class": "some-class-name"}

    INVALID_CONF_NOT_str = {"widget_hidden_input_css_class": object}

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF_None)
    def test_valid_config1(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF_str)
    def test_valid_config2(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=INVALID_CONF_NOT_str)
    def test_invalid_config1(self):
        self.assertCheckMessages([
            "django-gallery-widget-widget_hidden_input_css_class.E001"])


"""
    "prompt_alert_if_changed_on_window_reload": True,
"""


class CheckPromptAlert(CheckSettingsBase):
    msg_id_prefix = "django-gallery-widget-prompt_alert_if_changed_on_window_reload"

    VALID_CONF_None = {"prompt_alert_if_changed_on_window_reload": None}

    VALID_CONF_bool = {"prompt_alert_if_changed_on_window_reload": False}

    INVALID_CONF_NOT_bool = {"prompt_alert_if_changed_on_window_reload": object}

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF_None)
    def test_valid_config1(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=VALID_CONF_bool)
    def test_valid_config2(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_WIDGET_CONFIG=INVALID_CONF_NOT_bool)
    def test_invalid_config1(self):
        self.assertCheckMessages([
            "django-gallery-widget-prompt_alert_if_changed_on_window_reload.E001"])
