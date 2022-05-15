Quick Start
============

Installation
~~~~~~~~~~~~~~
You can install with pip from `PyPi <https://pypi.org/project/django-galleryfield/>`_ via::

    pip install django-galleryfield

Or for the latest dev version, via::

    pip install git+https://github.com/dzhuang/django-galleryfield.git


Python version
~~~~~~~~~~~~~~~~
Gallery-widget is compatible with Python 3 (3.6 or later were tested).

Dependencies
~~~~~~~~~~~~~~~~
Python dependencies:

-  Django 3.1 or later
-  `sorl-thumbnail <https://github.com/sorl/sorl-thumbnail>`_ (auto installed)
-  `pillow <https://github.com/python-imaging/Pillow>`_ (auto installed)


Static dependencies:

-  Bootstrap 3.4.1 (included)
-  jQuery 3.6 (included)
-  jQuery UI (included)
-  `blueimp/jQuery-File-Upload <https://github.com/blueimp/jQuery-File-Upload>`__
   (included)
-  `blueimp/Gallery <https://github.com/blueimp/Gallery>`__ (included)

-  `cropper <https://fengyuanchen.github.io/cropper>`_ by Chen Fengyuan (included)

The static dependencies were already included in the package.


Configurations
~~~~~~~~~~~~~~~~~~

- In ``settings.py``, add 3 lines in you ``INSTALLED_APP``:

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'sorl.thumbnail',
        'galleryfield',
        ...,
    )

    DJANGO_GALLERY_CONFIG = ...

- In ``urls.py``, add the following lines:

.. code-block:: python

    from django.urls import include, path

    urlpatterns += [path(r"images-handler/", include("galleryfield.urls"))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

- Sync the database::

    python manage.py migrate galleryfield



Run the demo
~~~~~~~~~~~~~
The best way to have a glance of how django-galleryfield works is to run the demo:

.. code-block:: bash

    git clone https://github.com/dzhuang/django-galleryfield.git
    cd django-galleryfield
    cd demo
    pip install -r requirements.txt
    cd ..
    python manage.py migrate
    python manage.py createsuperuser # Create a superuser account so that you can upload images
    python manage.py runserver

- In your browser navigate to http://127.0.0.1:8000/admin, login and then navigate back to  http://127.0.0.1:8000/.

.. note:: You might need to install JSON1 extension for SQLite for this the demo to run properly.
   See `Enabling JSON1 extension on SQLite <https://code.djangoproject.com/wiki/JSON1Extension>`_.
