========
Settings
========

Settings related to the package were included in a dict named ``DJANGO_GALLERY_FIELD_CONFIG``.

.. setting:: DJANGO_GALLERY_FIELD_CONFIG

DJANGO_GALLERY_FIELD_CONFIG
---------------------------------

Default:

.. code-block:: python

    {
        "assets": {
            "jquery.js": "jquery/dist/jquery.min.js",
            "jquery-ui.js": "jquery-ui-dist/jquery-ui.min.js",
           ...
            "extra_js": [],
            "extra_css": [],
        },

        "thumbnails": {
            "size": "120x120",
            "quality": 80
        },

        "widget_hidden_input_css_class": "django-galleryfield",
        "prompt_alert_if_changed_on_window_reload": True,
        "jquery_file_upload_ui_options": {
            "autoUpload": False,
            "imageMaxWidth": 1024,
            "imageMaxHeight": 1024,
            ...
        }
    }

See details below.

.. setting:: settings_default_assets

assets
~~~~~~~

Default:

.. code-block:: python

    {

        "jquery.js": "jquery/dist/jquery.min.js",
        "jquery-ui.js": "jquery-ui-dist/jquery-ui.min.js",
        ...
        "extra_js": [],
        "extra_css": []
    }

The first part is the static assets required to render the
:class:`galleryfield.widgets.GalleryWidget`.
The value includes 2 parts. The second part, i.e., ``extra_js`` and
``extra_css`` allow user to add customized static files when customize
the rendering of the widget. The first part is the static assets required to render
the :class:`galleryfield.widgets.GalleryWidget`. The default value for this part
is listed in ``galleryfield.defaults.DEFAULT_ASSETS``.

.. currentmodule:: galleryfield.default
.. autodata:: galleryfield.defaults.DEFAULT_ASSETS
   :annotation:
.. pprint:: galleryfield.defaults.DEFAULT_ASSETS


.. warning::
   This project relies heavily on CSS and JS frameworks/packages, so we strongly
   suggest using ``django-npm`` to manage the static assets for convenience. If
   you have other options, for example, not willing to have a local copy of those assets,
   you need to make sure ALL the items in ``galleryfield.defaults.DEFAULT_ASSET``
   were properly configured in this setting and
   can be accessed properly.

   BTW, trying to ignore some commonly used framework such as
   `Bootstrap` (because you already has it in your instance) will result in failure in
   rendering the widget in Admin.

.. setting:: settings_thumbnails

thumbnails
~~~~~~~~~~~
Default::

        "thumbnails": {
            "size": "120x120",
            "quality": 80
        },

We use `sorl.thumbnail <https://github.com/jazzband/sorl-thumbnail>`_ to generate the thumbnails
in the project. The term ``size`` correspond to
`geometry <https://sorl-thumbnail.readthedocs.io/en/latest/template.html#geometry>`_ in ``sorl.thumbnail``.
Currently, we accept the following format of size:

.. code-block:: python

    '120x80'
    (120, 80)  # same as '120x80'
    ('120', '80')  # same as '120x80'
    [120, 80]  # same as '120x80'
    ['120', '80'] # same as '120x80'
    120  # same as '120x120'


The ``size`` can be overridden when initializing :class:`galleryfield.widgets.GalleryWidget` via
:attr:`thumbnail_size`.

For quality, please refer to
`quality option <https://sorl-thumbnail.readthedocs.io/en/latest/template.html#quality>`_ in
`sorl.thumbnail <https://github.com/jazzband/sorl-thumbnail>`_.


.. setting:: jquery_file_upload_ui_options

jquery_file_upload_ui_options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The default value is listed in ``galleryfield.defaults.JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS``.

.. autodata:: galleryfield.defaults.JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS
   :annotation:
.. pprint:: galleryfield.defaults.JQUERY_FILE_UPLOAD_UI_DEFAULT_OPTIONS

The value can be overridden when initializing :class:`galleryfield.widgets.GalleryWidget` via
:attr:`jquery_file_upload_ui_options`.
Please refer to `available options <https://github.com/blueimp/jQuery-File-Upload/wiki/Options#general-options>`__
for the details and more options.

.. warning::
   Options ``previewMaxWidth`` and ``previewMaxHeight`` were ignored in favor of
   :setting:`thumbnail settings <settings_thumbnails>`.
   Option ``maxNumberOfFiles`` will be ignored and should be configured in the formfield.
   See example in :class:`galleryfield.fields.GalleryFormField`.
   Options ``fileInput``, ``paramName`` and ``singleFileUploads`` were also
   ignored (overridden).

