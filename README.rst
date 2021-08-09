django-gallery-widget
=====================

.. image:: https://codecov.io/gh/dzhuang/django-gallery-widget/branch/main/graph/badge.svg?token=W9BWM4A4RI :target: https://codecov.io/gh/dzhuang/django-gallery-widget


Django AJAX form widgets and model fields for multiple images upload with progress bar. Some of the ideas/code are inspired by `Django-jfu <https://github.com/Alem/django-jfu>`__ and `Django-files-widget <https://github.com/TND/django-files-widget>`__.

**This is currently an alpha release.**

Features
--------

-  Drag & drop file uploading via AJAX
-  Uploading multiple images with progress bar
-  A model fields with corresponding form fields and widgets: ``gallery.fields.GalleryField``
-  Image gallery widget with drag & drop reordering, client side crop before/after upload.
-  Integrates with Django Admin.

ScreenShots
-----------

-  Multiple image upload, sortable

.. image:: https://github.com/dzhuang/django-gallery-widget/raw/main/demo/static/demo/screen_upload.png
   :width: 70%
   :align: center

-  Client/Server side crop

.. image:: https://github.com/dzhuang/django-gallery-widget/raw/main/demo/static/demo/screen_crop.png
   :width: 70%
   :align: center

-  Easy Gallery render

.. image:: https://github.com/dzhuang/django-gallery-widget/raw/main/demo/static/demo/screen_detail.png
   :width: 70%
   :align: center

Quick Start
-----------

Requirements
~~~~~~~~~~~~

-  Django 3.1 or later
-  `sorl-thumbnail <https://github.com/sorl/sorl-thumbnail>`__
-  `pillow <https://github.com/python-imaging/Pillow>`__ (or PIL)
-  Bootstrap 3 or later (included)
-  jQuery 1.7 or later (included)
-  jQuery UI (included)
-  `blueimp/jQuery-File-Upload <https://github.com/blueimp/jQuery-File-Upload>`__
   (included)
-  `blueimp/Gallery <https://github.com/blueimp/Gallery>`__ (included)

Install
~~~~~~~

::

    pip install django-gallery-widget.git

In ``settings.py``
~~~~~~~~~~~~~~~~~~

::

    INSTALLED_APPS = (
        ...,
        'sorl.thumbnail',
        'gallery',
        ...,
    )

    DJANGO_GALLERY_CONFIG = ...

In ``urls.py``
~~~~~~~~~~~~~~

::

    path(r"gallery-handler/", include("gallery.urls")),

Run the demo
~~~~~~~~~~~~

::

    git clone https://github.com/dzhuang/django-gallery-widget.git
    cd django-gallery-widget
    cd demo
    pip install -r requirements.txt
    cd ..
    python manage.py migrate
    python manage.py createsuperuser # Create a superuser account so that you can upload images
    python manage.py runserver

Then in your browser navigate to http://127.0.0.1:8000/admin and login, then return to http://127.0.0.1:8000/.

**Notice**: You might need to install JSON1 extension for SQLite for this the demo to run properly. See `Enabling JSON1 extension on SQLite <https://code.djangoproject.com/wiki/JSON1Extension>`__.

License
-------

MIT

Credits
-------

-  `jQuery File
   Upload <https://github.com/blueimp/jQuery-File-Upload/wiki/Options>`__
-  `Django-files-widget <https://github.com/TND/django-files-widget>`__
   by Maarten ter Horst, which greatly inspired this project.
-  `Django-jfu <https://github.com/Alem/django-jfu>`__

Navigation
----------

Settings
~~~~~~~~

Django Gallery Widget related settings is a dict as shown below with
default value.

.. code:: Python


    DJANGO_GALLERY_WIDGET_CONFIG = {
        "assets": {
            "bootstrap.js": 'vendor/bootstrap/dist/js/bootstrap.min.js',
            "jquery.js": "vendor/jquery.min.js",
            ...
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

Model related default\_values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Django-Gallery-Widget has a built-in image Model ``gallery.models.BuiltInGalleryImage``, in which ``image`` is the target field of the gallery model. User can use this models without much modifying in their apps. See the demo app for details. With that built-in model, default views are applied with default urls (i.e, ``upload_handler_url_name``, ``fetch_url_name`` and ``crop_url_name``).

However, it is heavily suggested for developers to write your own image models, views, urls, and override those settings for your apps, especially in terms of permission considerations.

What are the difference as compared to peer apps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  `Django-files-widget <https://github.com/TND/django-files-widget>`__. In Django-files-widget, the files are managed and stored as ``string`` objects, which is actually the relative path of the files in the ``MEDIA_ROOT``. That means only a few user with granted permissions can upload/delete files uploaded to the server. In Django-Gallery-Widget, files are stored in ``imageField``, and it's possible to have better permission framework with regards to who can CRUD which images through views, and that expand the use case of the widget.

-  `Django-jfu <https://github.com/Alem/django-jfu>`__. It is a good demo of how to use Blueimp Jquery File Upload widget in Django. However, it currently only meet the demand of upload images via AJAX, not in terms of Gallery. And it has a long way for the demo to be integrated into an app, e.g., in terms of ``required``, ``readonly`` attribute of form fields.

TODOs
-----

-  Detailed Documentation
-  More demos

Known issues
------------

-  Css rendering of buttons in Admin.
-  Doesn't support svg because django ImageField can't handle it for now.
