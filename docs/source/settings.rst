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
        "bootstrap_version": 3,
        "assets": {
            "jquery": "path/or/url/to/jquery.js",
            "bootstrap_css": "path/or/url/to/bootstrap.css",
            "bootstrap_js": "path/or/url/to/bootstrap.js",
            "extra_js": [],
            "extra_css": [],
        },

        "thumbnails": {
            "size": "120x120",
            "quality": 80
        },

        "jquery_file_upload_ui_options": {
            "autoUpload": False,
            "imageMaxWidth": 1024,
            "imageMaxHeight": 1024,
            ...
        },

        "jquery_file_upload_ui_sortable_options": {
            "disabled": False,
            "delay": 300,
            "animation": 200,
            ...
        }

        "prompt_alert_if_changed_on_window_reload": True,
        "widget_hidden_input_css_class": "django-galleryfield",

    }

See details below.

.. setting:: settings_bootstrap_version

bootstrap_version
~~~~~~~~~~~~~~~~~~~

Default: 3

The value denotes the version of Twitter Bootstrap used by :ref:`GalleryWidget`.  Allow values include 3, 4 or 5.


.. setting:: settings_assets

assets
~~~~~~~

The assets needed for rendering :ref:`GalleryWidget`.

- ``jquery``: The path or url to `jQuery.js`. Defaults to ``https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js``.
- ``bootstrap_css``: The path or url to `bootstrap.css`, or a `dict` with `bootstrap_version` s as key, and path/url as value. Defaults to:

.. code-block:: python

    {
     3: "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.4.1/css/bootstrap.min.css",
     4: "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.1/css/bootstrap.min.css",
     5: "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/5.1.3/css/bootstrap.min.css",
    }

- ``bootstrap_js``: The path or url to `bootstrap.js`, or a `dict` with `bootstrap_version` s as key, and path/url as value. Defaults to:

.. code-block:: python

    {
     3: "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.4.1/css/bootstrap.min.js",
     4: "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.1/css/bootstrap.min.js",
     5: "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/5.1.3/css/bootstrap.min.js",
    }

- ``extra_js`` and ``extra_css`` allow user to add customized static files when customize
  the rendering of the widget. Both defaults to `[]`.


If you want to serve ``assets`` files locally, you can override those values using the relative path
of those files in `STATICFILES_DIRS <https://docs.djangoproject.com/en/dev/ref/settings/#std-setting-STATICFILES_DIRS>`__ .

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


.. warning::
   Options ``previewMaxWidth`` and ``previewMaxHeight`` were ignored in favor of
   :setting:`thumbnail settings <settings_thumbnails>`.
   Option ``maxNumberOfFiles`` will be ignored and should be configured in the formfield.
   See example in :class:`galleryfield.fields.GalleryFormField`.
   Options ``fileInput``, ``paramName`` and ``singleFileUploads`` were also
   ignored (overridden).


jquery_file_upload_ui_sortable_options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The default value is listed in ``galleryfield.defaults.JQUERY_FILE_UPLOAD_UI_DEFAULT_SORTABLE_OPTIONS``.

.. autodata:: galleryfield.defaults.JQUERY_FILE_UPLOAD_UI_DEFAULT_SORTABLE_OPTIONS
   :annotation:
.. pprint:: galleryfield.defaults.JQUERY_FILE_UPLOAD_UI_DEFAULT_SORTABLE_OPTIONS

prompt_alert_if_changed_on_window_reload
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: True

Whether prompt an alert when navigating away or closing the tablet/browser if there were changes
on ``GalleryField`` in the page.


widget_hidden_input_css_class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: "django-galleryfield"

The CSS classname of the hidden form field which actually recorded the value and changes of the ``GalleryField``.
