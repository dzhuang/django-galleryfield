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
-  django-npm (optional, for managing statics, you need to have ``npm`` installed in your OS)

Static dependencies:

-  Bootstrap 3
-  jQuery 1.7 or later
-  jQuery UI
-  `blueimp/jQuery-File-Upload <https://github.com/blueimp/jQuery-File-Upload>`_
-  `blueimp/Gallery <https://github.com/blueimp/Gallery>`_
-  `cropper <https://fengyuanchen.github.io/cropper>`_ by Chen Fengyuan

The static dependencies can be installed by command ``npm install``.


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

- We strongly propose using ``django-npm`` to manage the static dependencies,
  by adding the following lines in ``settings.py``:

.. code-block:: python

    from django.conf.global_settings import STATICFILES_FINDERS

    STATICFILES_FINDERS = tuple(STATICFILES_FINDERS) + ("npm.finders.NpmFinder",)


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
    npm install  # or yarn, install the CSS and JS modules
    python manage.py migrate
    python manage.py createsuperuser # Create a superuser account so that you can upload images
    python manage.py runserver

- In your browser navigate to http://127.0.0.1:8000/admin, login and then navigate back to  http://127.0.0.1:8000/.

.. note:: You might need to install JSON1 extension for SQLite for this the demo to run properly.
   See `Enabling JSON1 extension on SQLite <https://code.djangoproject.com/wiki/JSON1Extension>`_.
