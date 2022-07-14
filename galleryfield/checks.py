from django.apps import apps
from django.conf import settings
from django.core import checks

from galleryfield import defaults
from galleryfield.utils import (GENERIC_ERROR_PATTERN, INSTANCE_ERROR_PATTERN,
                                DJGalleryCriticalCheckMessage,
                                InvalidThumbnailFormat,
                                get_formatted_thumbnail_size)

DJANGO_GALLERY_FIELD_CONFIG = "DJANGO_GALLERY_FIELD_CONFIG"

ASSETS = "assets"
JQUERY = "jquery"
BOOTSTRAP_VERSION = "bootstrap_version"
BOOTSTRAP_CSS = "bootstrap_css"
BOOTSTRAP_JS = "bootstrap_js"
EXTRA_JS = "extra_js"
EXTRA_CSS = "extra_css"

THUMBNAILS = "thumbnails"
THUMBNAIL_SIZE = "size"
THUMBNAIL_QUALITY = "quality"

WIDGET_HIDDEN_INPUT_CSS_CLASS = "widget_hidden_input_css_class"

PROMPT_ALERT_IF_CHANGED_ON_WINDOW_RELOAD = (
    "prompt_alert_if_changed_on_window_reload")

JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS = (
    "jquery_file_upload_ui_options"
)

JQUERY_FILE_UPLOAD_UI_DEFAULT_SORTABLE_OPTIONS = (
    "jquery_file_upload_ui_sortable_options")

MAX_NUMBER_OF_FILES = "maxNumberOfFiles"
SINGLE_FILE_UPLOADS = "singleFileUploads"
PREVIEW_MAX_WIDTH = "previewMaxWidth"
PREVIEW_MAX_HEIGHT = "previewMaxHeight"


def register_galleryfield_settings_checks():
    checks.register(check_settings, "django_gallery_field_checks")


def check_settings(app_configs, **kwargs):
    errors = []

    if not apps.is_installed('sorl.thumbnail'):
        missing_app = checks.Error(
            "'sorl.thumbnail' must be in INSTALLED_APPS in order "
            "to generate thumbnail for gallery images.",
            id="django-galleryfield.E001",
        )
        errors.append(missing_app)

    conf = getattr(settings, "DJANGO_GALLERY_FIELD_CONFIG", None)
    if conf is None:
        return errors

    if not isinstance(conf, dict):
        errors.append(DJGalleryCriticalCheckMessage(
            msg=(INSTANCE_ERROR_PATTERN
                 % {"location": DJANGO_GALLERY_FIELD_CONFIG, "types": "dict"}),
            id="django-galleryfield.E002"
        ))
        return errors

    bootstrap_version = conf.get(BOOTSTRAP_VERSION, None)
    if bootstrap_version is not None:
        try:
            ver = int(bootstrap_version)
            assert ver == float(bootstrap_version)
        except Exception:
            errors.append(DJGalleryCriticalCheckMessage(
                msg=f"'{BOOTSTRAP_VERSION}' in {DJANGO_GALLERY_FIELD_CONFIG}: "
                    f"'{bootstrap_version}' is not a valid version number. "
                    f"Please use 3, 4 or 5",
                id="django-galleryfield-bootstrap_version.E001"
            ))
        else:
            if ver < defaults.DEFAULT_BOOTSTRAP_VERSION:
                errors.append(DJGalleryCriticalCheckMessage(
                    msg=f"'{BOOTSTRAP_VERSION}' in {DJANGO_GALLERY_FIELD_CONFIG}: "
                        f"version number should not be lower than "
                        f"{defaults.DEFAULT_BOOTSTRAP_VERSION}, "
                        f"while got '{bootstrap_version}'.",
                    id="django-galleryfield-bootstrap_version.E002"
                ))

    assets = conf.get(ASSETS, None)
    if assets is not None:
        if not isinstance(assets, dict):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": f"'{ASSETS}' in '{DJANGO_GALLERY_FIELD_CONFIG}'",
                        "types": "dict"}),
                id="django-galleryfield-assets.E001"
            ))
        else:
            assets_copy = assets.copy()
            extra_js = assets_copy.pop(EXTRA_JS, None)
            if extra_js is not None:
                if not isinstance(extra_js, list):
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(INSTANCE_ERROR_PATTERN
                             % {"location": f"'{EXTRA_JS}' in '{ASSETS}' in "
                                            f"'{DJANGO_GALLERY_FIELD_CONFIG}'",
                                "types": "str"}),
                        id="django-galleryfield-assets.E002"
                    ))
                else:
                    for js_name in extra_js:
                        if not isinstance(js_name, str):
                            errors.append(DJGalleryCriticalCheckMessage(
                                msg=(INSTANCE_ERROR_PATTERN % {
                                    "location":
                                        f"'{js_name}' in '{EXTRA_JS}' in '{ASSETS}'"
                                        f" in '{DJANGO_GALLERY_FIELD_CONFIG}'",
                                    "types": "str"}),
                                id="django-galleryfield-assets.E003"
                            ))

            extra_css = assets_copy.pop(EXTRA_CSS, None)
            if extra_css is not None:
                if not isinstance(extra_css, list):
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(INSTANCE_ERROR_PATTERN
                             % {"location": f"'{EXTRA_CSS}' in '{ASSETS}' "
                                            f"in '{DJANGO_GALLERY_FIELD_CONFIG}'",
                                "types": "str"}),
                        id="django-galleryfield-assets.E004"
                    ))
                else:
                    for css_name in extra_css:
                        if not isinstance(css_name, str):
                            errors.append(DJGalleryCriticalCheckMessage(
                                msg=(INSTANCE_ERROR_PATTERN % {
                                    "location":
                                        f"'{css_name}' in '{EXTRA_CSS}' in "
                                        f"'{ASSETS}' in "
                                        f"'{DJANGO_GALLERY_FIELD_CONFIG}'",
                                    "types": "str"}),
                                id="django-galleryfield-assets.E005"
                            ))

            for asset_name, asset_value in assets_copy.items():
                if asset_name not in [JQUERY, BOOTSTRAP_CSS, BOOTSTRAP_JS]:
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=("Unknown asset key '%(asset)s' in %(location)s, "
                             "available choices are %(choices)s."
                             % {"asset": asset_name,
                                "location": (
                                    f"'{ASSETS}' in '{DJANGO_GALLERY_FIELD_CONFIG}'"
                                ),
                                "choices": ", ".join(
                                    [JQUERY, BOOTSTRAP_CSS, BOOTSTRAP_JS,
                                     EXTRA_CSS, EXTRA_JS])
                                }
                             ),
                        id="django-galleryfield-assets.E006"
                    ))

    thumbnails = conf.get(THUMBNAILS, None)
    if thumbnails is not None:
        if not isinstance(thumbnails, dict):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": f"'{THUMBNAILS}' in "
                                    f"'{DJANGO_GALLERY_FIELD_CONFIG}'",
                        "types": "dict"}),
                id="django-galleryfield-thumbnails.E001"
            ))
        else:
            thumbnail_size = thumbnails.get(THUMBNAIL_SIZE, None)
            try:
                get_formatted_thumbnail_size(
                    thumbnail_size, name=THUMBNAIL_SIZE)
            except Exception as e:
                if isinstance(e, InvalidThumbnailFormat):
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(GENERIC_ERROR_PATTERN
                             % {"location": f"'{THUMBNAIL_SIZE}' in '{THUMBNAILS}' "
                                            f"in '{DJANGO_GALLERY_FIELD_CONFIG}'",
                                "error_type": type(e).__name__,
                                "error_str": (
                                        f"'{THUMBNAIL_SIZE}' must be an int, "
                                        f"or a string of int, "
                                        "or in the form of 80x60, or a list, e.g,"
                                        " [80, 60], or a tuple (80, 60)")}
                             ),
                        id="django-galleryfield-thumbnails.E003"
                    ))
                else:
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(GENERIC_ERROR_PATTERN
                             % {"location": f"'{THUMBNAIL_SIZE}' in '{THUMBNAILS}' "
                                            f"in '{DJANGO_GALLERY_FIELD_CONFIG}'",
                                "error_type": type(e).__name__,
                                "error_str": str(e)}
                             ),
                        id="django-galleryfield-thumbnails.E002"
                    ))

            thumbnail_quality = thumbnails.get(THUMBNAIL_QUALITY, None)
            if thumbnail_quality is not None:
                try:
                    quality = float(thumbnail_quality)
                except Exception as e:
                    errors.append(DJGalleryCriticalCheckMessage(
                        msg=(GENERIC_ERROR_PATTERN
                             % {"location": f"'{THUMBNAIL_QUALITY}' in "
                                            f"'{THUMBNAILS}' in "
                                            f"'{DJANGO_GALLERY_FIELD_CONFIG}'",
                                "error_type": type(e).__name__,
                                "error_str": str(e)}
                             ),
                        id="django-galleryfield-thumbnails.E004"
                    ))
                else:
                    if quality < 0 or quality > 100:
                        errors.append(DJGalleryCriticalCheckMessage(
                            msg=(GENERIC_ERROR_PATTERN
                                 % {"location": f"'{THUMBNAIL_QUALITY}' in "
                                                f"'{THUMBNAILS}' in "
                                                f"'{DJANGO_GALLERY_FIELD_CONFIG}'",
                                    "error_type": TypeError.__name__,
                                    "error_str":
                                        "Thumbnail quality should be "
                                        "between 0 and 100"}
                                 ),
                            id="django-galleryfield-thumbnails.E005"
                        ))

    jfu_options = conf.get(JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS, None)
    if jfu_options is not None:
        if not isinstance(jfu_options, dict):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": f"'{JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS}' in "
                                    f"'{DJANGO_GALLERY_FIELD_CONFIG}'",
                        "types": "dict"}),
                id="django-galleryfield-jquery_file_upload_ui_options.E001"
            ))
        else:
            if MAX_NUMBER_OF_FILES in jfu_options:
                errors.append(checks.Warning(
                    msg=("%(location)s will be ignored, that is configured in "
                         "the formfield the GalleryWidget is serving, with the "
                         "param name `max_number_of_images`"
                         % {"location": f"option '{MAX_NUMBER_OF_FILES}' in "
                                        f"'{JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS}'"
                                        f" in '{DJANGO_GALLERY_FIELD_CONFIG}'"}),
                    id="django-galleryfield-jquery_file_upload_ui_options.W001"
                ))

            if (SINGLE_FILE_UPLOADS in jfu_options
                    # Some user might use "false" string to represent False
                    and str(jfu_options[SINGLE_FILE_UPLOADS]).lower() == "false"):
                errors.append(checks.Warning(
                    msg=("%(location)s set to False is not allowed and will"
                         "be ignored. "
                         % {"location": f"option '{SINGLE_FILE_UPLOADS}' in "
                                        f"'{JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS}'"
                                        f" in '{DJANGO_GALLERY_FIELD_CONFIG}'"}),
                    id="django-galleryfield-jquery_file_upload_ui_options.W002"
                ))

            if PREVIEW_MAX_WIDTH in jfu_options or PREVIEW_MAX_HEIGHT in jfu_options:
                errors.append(checks.Warning(
                    msg=("%(location)s will be ignored. By preview size, we mean "
                         "the thumbnail size in the GalleryWidget UI, so you should "
                         "set the value in %(right_place)s."
                         % {"location": f"option '{PREVIEW_MAX_WIDTH}' or "
                                        f"'{PREVIEW_MAX_HEIGHT}' in "
                                        f"'{JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS}'"
                                        f" in '{DJANGO_GALLERY_FIELD_CONFIG}'",
                            "right_place": f"'{THUMBNAIL_SIZE}' in '{THUMBNAILS}' "
                                           f"in '{DJANGO_GALLERY_FIELD_CONFIG}'"}),
                    id="django-galleryfield-jquery_file_upload_ui_options.W003"
                ))

    sortable_options = conf.get(JQUERY_FILE_UPLOAD_UI_DEFAULT_SORTABLE_OPTIONS, None)
    if sortable_options is not None:
        if not isinstance(sortable_options, dict):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {
                         "location":
                             f"'{JQUERY_FILE_UPLOAD_UI_DEFAULT_SORTABLE_OPTIONS}'"
                             f" in '{DJANGO_GALLERY_FIELD_CONFIG}'",
                         "types": "dict"}),
                id="django-galleryfield-jquery_file_upload_ui_sortable_options.E001"
            ))

    widget_hidden_input_css_class = conf.get(WIDGET_HIDDEN_INPUT_CSS_CLASS, None)

    if widget_hidden_input_css_class is not None:
        if not isinstance(widget_hidden_input_css_class, str):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": f"'{WIDGET_HIDDEN_INPUT_CSS_CLASS}' in "
                                    f"'{DJANGO_GALLERY_FIELD_CONFIG}'",
                        "types": "str"}),
                id="django-galleryfield-widget_hidden_input_css_class.E001"
            ))

    prompt_alert_if_changed_on_window_reload = conf.get(
        PROMPT_ALERT_IF_CHANGED_ON_WINDOW_RELOAD, None)

    if prompt_alert_if_changed_on_window_reload is not None:
        if not isinstance(prompt_alert_if_changed_on_window_reload, bool):
            errors.append(DJGalleryCriticalCheckMessage(
                msg=(INSTANCE_ERROR_PATTERN
                     % {"location": f"'{PROMPT_ALERT_IF_CHANGED_ON_WINDOW_RELOAD}' "
                                    f"in '{DJANGO_GALLERY_FIELD_CONFIG}'",
                        "types": "bool"}),
                id="django-galleryfield-prompt_alert_if_changed_on_window_reload"
                   ".E001"
            ))

    return errors
