Quick Start
============

Installation
~~~~~~~~~~~~~~
You can install with pip from PyPi via::

    pip install django-gallery-widget

Or for the latest dev version, via::

    pip install git+https://github.com/dzhuang/django-gallery-widget.git


Python version
~~~~~~~~~~~~~~~~
Gallery-widget is compatible with Python 3 (3.6 or later were tested).

Dependencies
~~~~~~~~~~~~~~~~
Python dependencies include:
-  Django 3.1 or later
-  `sorl-thumbnail <https://github.com/sorl/sorl-thumbnail>`_ (auto installed)
-  `pillow <https://github.com/python-imaging/Pillow>`_ (auto installed)
-  django-npm (for managing statics, you need to have ``npm`` installed in your OS)

Static dependencies which will can be installed by ``npm``:
-  Bootstrap 3 or later (included)
-  jQuery 1.7 or later (included)
-  jQuery UI (included)
-  `blueimp/jQuery-File-Upload <https://github.com/blueimp/jQuery-File-Upload>`__
   (included)
-  `blueimp/Gallery <https://github.com/blueimp/Gallery>`__ (included)
-  `cropper <https://fengyuanchen.github.io/cropper>`_ by Chen Fengyuan(included)


Configurations
~~~~~~~~~~~~~~~~~~

- In ``settings.py``, add 3 lines in you ``INSTALLED_APP``:

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'sorl.thumbnail',
        'gallery_widget',
        ...,
    )

    DJANGO_GALLERY_CONFIG = ...

- We strongly propose using ``django-npm`` to manage the static dependencies,
  add the following lines in ``settings.py``:

.. code-block:: python

    from django.conf.global_settings import STATICFILES_FINDERS

    STATICFILES_FINDERS = tuple(STATICFILES_FINDERS) + ("npm.finders.NpmFinder",)


- In ``urls.py``, add the following lines:

.. code-block:: python

    from django.urls import include, path

    urlpatterns += [path(r"gallery-handler/", include("gallery_widget.urls"))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

- The sync the database::

    python manage.py migrate gallery_widget



Run the demo
~~~~~~~~~~~~~
The best way to have a glance of how django-gallery-widget works is to run the demo:

.. code-block:: bash

    git clone https://github.com/dzhuang/django-gallery-widget.git
    cd django-gallery-widget
    cd demo
    pip install -r requirements.txt
    cd ..
    npm install  # or yarn, install the CSS and JS modules
    python manage.py migrate
    python manage.py createsuperuser # Create a superuser account so that you can upload images
    python manage.py runserver

- In your browser navigate to http://127.0.0.1:8000/admin, login and navigate to  http://127.0.0.1:8000/.

.. note:: You might need to install JSON1 extension for SQLite for this the demo to run properly.
   See `Enabling JSON1 extension on SQLite <https://code.djangoproject.com/wiki/JSON1Extension>`_.
