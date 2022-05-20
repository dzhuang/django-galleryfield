from django.test import SimpleTestCase
from django.test.utils import override_settings


class CheckSettingsBase(SimpleTestCase):
    @property
    def func(self):
        from galleryfield.checks import check_settings
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
    msg_id_prefix = "django-galleryfield"
    VALID_CONF_None = None
    VALID_CONF_Dict = {}
    INVALID_CONF_EMPTY_LIST = []
    INVALID_CONF_SPACES = " "

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_None)
    def test_valid_config1(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_Dict)
    def test_valid_config2(self):
        self.assertCheckMessages([])

    @override_settings(INSTALLED_APPS=['galleryfield', 'demo'])
    def test_invalid_config1(self):
        self.assertCheckMessages(["django-galleryfield.E001"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_EMPTY_LIST)
    def test_invalid_config2(self):
        self.assertCheckMessages(["django-galleryfield.E002"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_SPACES)
    def test_invalid_config3(self):
        self.assertCheckMessages(["django-galleryfield.E002"])


"""
DJANGO_GALLERY_FIELD_CONFIG = {
    "assets": {
        "jquery": 'vendor/jquery/dist/js/jquery.min.js'
        "bootstrap_js": 'vendor/bootstrap/dist/js/bootstrap.min.js',
        "bootstrap_css": "vendor/bootstrap/dist/css/bootstrap.min.css",
        "extra_js": [],
        "extra_css": [],
    },
    "thumbnails": {
        "size": 120,
        "quality": 80
    },
    jquery_file_upload_ui_options: {},
    "widget_hidden_input_css_class": "django-galleryfield",
    "prompt_alert_if_changed_on_window_reload": True,
}
"""


class CheckAssets(CheckSettingsBase):
    msg_id_prefix = "django-galleryfield-assets"

    VALID_CONF_None = {"assets": None}

    VALID_CONF_Dict = {"assets": dict()}

    VALID_CONF1 = {
        "assets": {
            "extra_js": ["some/js"],
            "extra_css": ["some/css"],
        },
    }

    VALID_CONF2 = {
        "assets": {
            "jquery": "foo",
            "bootstrap_css": "bar",
            "bootstrap_js": "bar",
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

    INVALID_CONF_NOT_Dict = {
        "assets": object
    }

    INVALID_CONF_EXTRA_JS = {
        "assets": {
            "extra_js": "extra_js",
        },
    }

    INVALID_CONF_UNKNOWN = {
        "assets": {
            # hyphen instead of underscore
            "bootstrap-js": "bar",
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

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_None)
    def test_valid_config1(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_Dict)
    def test_valid_config2(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF1)
    def test_valid_config3(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF2)
    def test_valid_config4(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_EXTRA_None)
    def test_valid_config5(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_NOT_Dict)
    def test_invalid_config01(self):
        self.assertCheckMessages(["django-galleryfield-assets.E001"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_EXTRA_JS)
    def test_invalid_config02(self):
        self.assertCheckMessages(["django-galleryfield-assets.E002"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_EXTRA_CSS)
    def test_invalid_config03(self):
        self.assertCheckMessages(["django-galleryfield-assets.E004"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_EXTRA_JS_ELE)
    def test_invalid_config04(self):
        self.assertCheckMessages(["django-galleryfield-assets.E003",
                                  "django-galleryfield-assets.E003"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_EXTRA_CSS_ELE)
    def test_invalid_config05(self):
        self.assertCheckMessages(["django-galleryfield-assets.E005",
                                  "django-galleryfield-assets.E005"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_UNKNOWN)
    def test_invalid_config06(self):
        self.assertCheckMessages(["django-galleryfield-assets.E006"])


"""
    "thumbnails": {
        "size": 120,
        "quality": 80
    },
"""


class CheckThumbnails(CheckSettingsBase):
    msg_id_prefix = "django-galleryfield-thumbnails"

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

    VALID_CONF_int_tuple = {
        "thumbnails": {
            "size": (20, 80),
        },
    }

    VALID_CONF_int_list = {
        "thumbnails": {
            "size": (20, 80),
        },
    }

    VALID_CONF_str_tuple = {
        "thumbnails": {
            "size": ("20", "80"),
        },
    }

    VALID_CONF_str_list = {
        "thumbnails": {
            "size": ["20", "80"],
        },
    }

    VALID_CONF_x = {
        "thumbnails": {
            "size": "20x80",
        },
    }

    VALID_CONF_X = {
        "thumbnails": {
            "size": "20x80",
        },
    }

    VALID_CONF_CONTAINS_SPACES = {
        "thumbnails": {
            "size": " 20 x 80 ",
        },
    }

    VALID_CONF_CAN_CONVERT_TO_NUMBER = {
        "thumbnails": {
            "size": "40",
            "quality": "80"
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

    INVALID_CONF_NEGATIVE_LIST = {
        "thumbnails": {
            "size": [-100, 100],
        },
    }

    INVALID_CONF_NEGATIVE_STR_LIST = {
        "thumbnails": {
            "size": ["-100", "100"],
        },
    }

    INVALID_CONF_NEGATIVE_TUPLE = {
        "thumbnails": {
            "size": ("-100", "100"),
        },
    }

    INVALID_CONF_EMPT_STR = {
        "thumbnails": {
            "size": "       ",
        },
    }

    INVALID_CONF_CONTAINS_3_tuple = {
        "thumbnails": {
            "size": (100, 200, 300),
        },
    }

    INVALID_CONF_CONTAINS_2_x = {
        "thumbnails": {
            "size": "100x200x300",
        },
    }

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_None)
    def test_valid_config1(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_Dict)
    def test_valid_config2(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF)
    def test_valid_config3(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_ALL_None)
    def test_valid_config4(self):
        self.assertCheckMessages([])

    @override_settings(
        DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_CAN_CONVERT_TO_NUMBER)
    def test_valid_config5(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_int_tuple)
    def test_valid_config6(self):
        self.assertCheckMessages([])

    @override_settings(
        DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_str_list)
    def test_valid_config7(self):
        self.assertCheckMessages([])

    @override_settings(
        DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_int_list)
    def test_valid_config8(self):
        self.assertCheckMessages([])

    @override_settings(
        DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_x)
    def test_valid_config9(self):
        self.assertCheckMessages([])

    @override_settings(
        DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_X)
    def test_valid_config10(self):
        self.assertCheckMessages([])

    @override_settings(
        DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_CONTAINS_SPACES)
    def test_valid_config11(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_NOT_Dict)
    def test_invalid_config1(self):
        self.assertCheckMessages(["django-galleryfield-thumbnails.E001"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_NOT_NUMBER)
    def test_invalid_config2(self):
        self.assertCheckMessages([
            "django-galleryfield-thumbnails.E003",
            "django-galleryfield-thumbnails.E004"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_NEGATIVE)
    def test_invalid_config3(self):
        self.assertCheckMessages([
            "django-galleryfield-thumbnails.E003",
            "django-galleryfield-thumbnails.E005"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_NEGATIVE_LIST)
    def test_invalid_config4(self):
        self.assertCheckMessages([
            "django-galleryfield-thumbnails.E003"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_NEGATIVE_TUPLE)
    def test_invalid_config5(self):
        self.assertCheckMessages([
            "django-galleryfield-thumbnails.E003"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_NEGATIVE_STR_LIST)
    def test_invalid_config6(self):
        self.assertCheckMessages([
            "django-galleryfield-thumbnails.E003"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_EMPT_STR)
    def test_invalid_config7(self):
        self.assertCheckMessages([
            "django-galleryfield-thumbnails.E002"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_CONTAINS_3_tuple)
    def test_invalid_config8(self):
        self.assertCheckMessages([
            "django-galleryfield-thumbnails.E003"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_CONTAINS_2_x)
    def test_invalid_config9(self):
        self.assertCheckMessages([
            "django-galleryfield-thumbnails.E003"])


"""
    jquery_file_upload_ui_options: {},
"""

MAX_NUMBER_OF_FILES = "maxNumberOfFiles"
SINGLE_FILE_UPLOADS = "singleFileUploads"
PREVIEW_MAX_WIDTH = "previewMaxWidth"
PREVIEW_MAX_HEIGHT = "previewMaxHeight"


class CheckJqueryFileUploadUiOptions(CheckSettingsBase):
    msg_id_prefix = "django-galleryfield-jquery_file_upload_ui_options"

    VALID_CONF_None = {"jquery_file_upload_ui_options": None}

    VALID_CONF_Dict = {"jquery_file_upload_ui_options": dict()}

    VALID_CONF = {
        "jquery_file_upload_ui_options": {
            "autoUpload": False
        }
    }

    WARN_CONF_MAX_NUMBER_OF_FILES = {
        "jquery_file_upload_ui_options": {
            "maxNumberOfFiles": 20
        }
    }

    WARN_CONF_SINGLE_FILE_UPLOADS_FALSE = {
        "jquery_file_upload_ui_options": {
            "singleFileUploads": False
        }
    }

    WARN_CONF_SINGLE_FILE_UPLOADS_FALSE_STRING = {
        "jquery_file_upload_ui_options": {
            "singleFileUploads": "false"
        }
    }

    NO_WARN_CONF_SINGLE_FILE_UPLOADS_TRUE = {
        "jquery_file_upload_ui_options": {
            "singleFileUploads": True
        }
    }

    WARN_CONF_PREVIEW_MAX_WIDTH = {
        "jquery_file_upload_ui_options": {
            "previewMaxWidth": 120
        }
    }

    WARN_CONF_PREVIEW_MAX_HEIGHT = {
        "jquery_file_upload_ui_options": {
            "previewMaxHeight": 180
        }
    }

    INVALID_CONF_NOT_Dict = {"jquery_file_upload_ui_options": object}

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_None)
    def test_valid_config1(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_Dict)
    def test_valid_config2(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF)
    def test_valid_config3(self):
        self.assertCheckMessages([])

    @override_settings(
        DJANGO_GALLERY_FIELD_CONFIG=NO_WARN_CONF_SINGLE_FILE_UPLOADS_TRUE)
    def test_valid_config4(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_NOT_Dict)
    def test_item_not_dict(self):
        self.assertCheckMessages(
            ["django-galleryfield-jquery_file_upload_ui_options.E001"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=WARN_CONF_MAX_NUMBER_OF_FILES)
    def test_item_warned_max_number_of_files(self):
        self.assertCheckMessages(
            ["django-galleryfield-jquery_file_upload_ui_options.W001"])

    @override_settings(
        DJANGO_GALLERY_FIELD_CONFIG=WARN_CONF_SINGLE_FILE_UPLOADS_FALSE)
    def test_warn_single_upload_false_1(self):
        self.assertCheckMessages(
            ["django-galleryfield-jquery_file_upload_ui_options.W002"])

    @override_settings(
        DJANGO_GALLERY_FIELD_CONFIG=WARN_CONF_SINGLE_FILE_UPLOADS_FALSE_STRING)
    def test_warn_single_upload_false_2(self):
        self.assertCheckMessages(
            ["django-galleryfield-jquery_file_upload_ui_options.W002"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=WARN_CONF_PREVIEW_MAX_HEIGHT)
    def test_warn_preview_max_height(self):
        self.assertCheckMessages(
            ["django-galleryfield-jquery_file_upload_ui_options.W003"])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=WARN_CONF_PREVIEW_MAX_WIDTH)
    def test_warn_preview_max_width(self):
        self.assertCheckMessages(
            ["django-galleryfield-jquery_file_upload_ui_options.W003"])


"""
    "widget_hidden_input_css_class": "django-galleryfield",
"""


class CheckMultifieldCssClassBasename(CheckSettingsBase):
    msg_id_prefix = "django-galleryfield-widget_hidden_input_css_class"

    VALID_CONF_None = {"widget_hidden_input_css_class": None}

    VALID_CONF_str = {"widget_hidden_input_css_class": "some-class-name"}

    INVALID_CONF_NOT_str = {"widget_hidden_input_css_class": object}

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_None)
    def test_valid_config1(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_str)
    def test_valid_config2(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_NOT_str)
    def test_invalid_config1(self):
        self.assertCheckMessages([
            "django-galleryfield-widget_hidden_input_css_class.E001"])


"""
    "prompt_alert_if_changed_on_window_reload": True,
"""


class CheckPromptAlert(CheckSettingsBase):
    msg_id_prefix = "django-galleryfield-prompt_alert_if_changed_on_window_reload"

    VALID_CONF_None = {"prompt_alert_if_changed_on_window_reload": None}

    VALID_CONF_bool = {"prompt_alert_if_changed_on_window_reload": False}

    INVALID_CONF_NOT_bool = {"prompt_alert_if_changed_on_window_reload": object}

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_None)
    def test_valid_config1(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=VALID_CONF_bool)
    def test_valid_config2(self):
        self.assertCheckMessages([])

    @override_settings(DJANGO_GALLERY_FIELD_CONFIG=INVALID_CONF_NOT_bool)
    def test_invalid_config1(self):
        self.assertCheckMessages([
            "django-galleryfield-prompt_alert_if_changed_on_window_reload.E001"])
