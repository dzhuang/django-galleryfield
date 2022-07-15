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
``django-galleryfield`` is compatible with Python 3 (3.6 or later were tested).

Dependencies
~~~~~~~~~~~~~~~~
Python dependencies:

-  Django 3.1 or later
-  `sorl-thumbnail <https://github.com/sorl/sorl-thumbnail>`_ (auto installed)
-  `pillow <https://github.com/python-imaging/Pillow>`_ (auto installed)


Static dependencies:

-  Bootstrap (CDN URLs included)
-  jQuery 3.6 (CDN URL included)
-  jQuery UI (included)
-  `blueimp/jQuery-File-Upload <https://github.com/blueimp/jQuery-File-Upload>`__ by Sebastian Tschan (included)
-  `blueimp/Gallery <https://github.com/blueimp/Gallery>`__ by Sebastian Tschan (included)
-  `cropper <https://fengyuanchen.github.io/cropper>`__ by Chen Fengyuan (included)
-  `SortableJS/Sortable <https://github.com/SortableJS/Sortable>`__ (included)
-  `FontAwesome Icons <https://github.com/FortAwesome/Font-Awesome>`__ (included)
-  `Material Design Icons <https://github.com/Templarian/MaterialDesign-Webfont>`__ (included)
-  `Subset-iconfont <https://github.com/dzhuang/subset-iconfont>`__ by dzhuang (included)


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

Usage in Views
~~~~~~~~~~~~~~~

To correctly render ``GalleryField`` in general views, you are required to include
``bootstrap.css``, ``jQuery.js`` and ``bootstrap.js`` (or their minified version),
with the exact order, in page head. Notice that the major version of Twitter Bootstrap
should be of the same version with the version in
``DJANGO_GALLERY_FIELD_CONFIG["bootstrap_version"]``, which defaults to 3.

Note: To prevent multiple click on form submit buttons, you can add ``gallery-widget-submit-button``
CSS classname to the submit buttons of the form.


Usage in Admin
~~~~~~~~~~~~~~~

To correctly render ``GalleryField`` in ``admin``,  the model form should be instantiated with
``galleryfield.mixins.GalleryFormMediaMixin``. For example, if the Gallery model is ``MyGallery``,
the snippet follows:

.. snippet:: python
   :filename: my_app/admin.py

    from django import forms
    from django.contrib import admin

    from my_app.models import MyGallery
    from galleryfield.mixins import GalleryFormMediaMixin


    class MyGalleryAdminForm(GalleryFormMediaMixin, forms.ModelForm):
        class Meta:
            model = MyGallery
            exclude = ()


    class MyGalleryAdmin(admin.ModelAdmin):
        form = MyGalleryAdminForm


    admin.site.register(MyGallery, MyGalleryAdmin)
