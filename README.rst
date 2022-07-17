django-galleryfield
=====================

.. image:: https://codecov.io/gh/dzhuang/django-galleryfield/branch/main/graph/badge.svg?token=W9BWM4A4RI
   :target: https://codecov.io/gh/dzhuang/django-galleryfield
.. image:: https://github.com/dzhuang/django-galleryfield/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/dzhuang/django-galleryfield/tree/main
.. image:: https://badge.fury.io/py/django-galleryfield.svg
   :target: https://badge.fury.io/py/django-galleryfield
.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
   :target: https://pycqa.github.io/isort/
.. image:: https://readthedocs.org/projects/django-galleryfield/badge/?version=latest
   :target: https://django-galleryfield.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


Django model fields ``GalleryField`` with AJAX form widgets and for multiple images upload with progress bar.
This package is **NOT** about how to elegantly render multiple images in a page, but how to CRUD multiple
images in a model field, which makes it possible for easy permission control.


Features
--------

-  A model field ``GalleryField``, and its formfield ``GalleryFormField`` along with the default widget ``GalleryWidget``.
-  Drag & drop file uploading via AJAX
-  Uploading multiple images with progress bar
-  Drag & drop reordering, client / server side crop before/after upload.
-  Integrates with Django Admin.
-  Each Image uploaded will be saved in an image model. That might be considered, by some user,
   a draw back. However, that makes it possible to delete the `orphan` images from the server (see in FAQ).

ScreenShots
-----------

-  Multiple image upload, sortable

.. image:: https://raw.githubusercontent.com/dzhuang/django-galleryfield/main/demo/static/demo/screen_upload.png
   :width: 70%
   :align: center

-  Client/Server side crop

.. image:: https://raw.githubusercontent.com/dzhuang/django-galleryfield/main/demo/static/demo/screen_crop.png
   :width: 70%
   :align: center

-  Easy Gallery render

.. image:: https://raw.githubusercontent.com/dzhuang/django-galleryfield/main/demo/static/demo/screen_detail.png
   :width: 70%
   :align: center


Quick Start
-----------

Requirements
~~~~~~~~~~~~

-  Django 3.1 or later
-  `sorl-thumbnail <https://github.com/sorl/sorl-thumbnail>`__
-  `pillow <https://github.com/python-imaging/Pillow>`__ (or PIL)


Install
~~~~~~~

::

    pip install django-galleryfield

Usage
~~~~~~~~~~~~~~~~~~

- In ``settings.py``, add 3 lines in you ``INSTALLED_APP``:

::

    INSTALLED_APPS = (
        ...,
        'sorl.thumbnail',
        'galleryfield',
        ...,
    )

    DJANGO_GALLERY_CONFIG = ...


- In ``urls.py``, add the following lines:

::

    from django.urls import include, path

    urlpatterns += [path(r"gallery-handler/", include("galleryfield.urls"))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


Run the demo
~~~~~~~~~~~~~~~~~~

::

    git clone https://github.com/dzhuang/django-galleryfield.git
    cd django-galleryfield
    cd demo
    pip install -r requirements.txt
    cd ..
    python manage.py migrate
    python manage.py createsuperuser # Create a superuser account so that you can upload images
    python manage.py runserver

- In your browser navigate to http://127.0.0.1:8000/admin, login and navigate to  http://127.0.0.1:8000/.

.. note:: You might need to install JSON1 extension for SQLite for this the demo to run properly. See `Enabling JSON1 extension on SQLite <https://code.djangoproject.com/wiki/JSON1Extension>`__.

Online documentation
~~~~~~~~~~~~~~~~~~~~~~
Please visit https://django-galleryfield.readthedocs.io for the documentation.

Contribute to the project
~~~~~~~~~~~~~~~~~~~~~~~~~~
See `Contribution guide <./docs/source/contribute.rst>`__.


License
-------------
Released under the `MIT license <./LICENSE.txt>`__.
