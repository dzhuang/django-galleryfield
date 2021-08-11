django-gallery-widget
=====================

.. image:: https://codecov.io/gh/dzhuang/django-gallery-widget/branch/main/graph/badge.svg?token=W9BWM4A4RI
   :target: https://codecov.io/gh/dzhuang/django-gallery-widget
.. image:: https://github.com/dzhuang/django-gallery-widget/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/dzhuang/django-gallery-widget/tree/main
.. image:: https://badge.fury.io/py/django-gallery-widget.svg
   :target: https://badge.fury.io/py/django-gallery-widget


Django AJAX form widgets and model fields for multiple images upload with progress bar. This package is **NOT** about
how to elegantly render multiple images in a page, but how to CRUD multiple images in a model field, which makes
it possible for easy permission control.


Features
--------

-  A model field ``GalleryField``, and its formfield ``GalleryFormField`` along with the default widget ``GalleryWidget``.
-  Drag & drop file uploading via AJAX
-  Uploading multiple images with progress bar
-  Drag & drop reordering, client / server side crop before/after upload.
-  Integrates with Django Admin.
-  Each Image uploaded will be saved in an image model. That might be considered, by some user,
   a draw back. However, that makes it possible to delete the `orpha` images from the server (see in FAQ).

ScreenShots
-----------

-  Multiple image upload, sortable

.. image:: https://github.com/dzhuang/django-gallery-widget/blob/main/demo/static/demo/screen_upload.png
   :width: 70%
   :align: center

-  Client/Server side crop

.. image:: https://github.com/dzhuang/django-gallery-widget/blob/main/demo/static/demo/screen_crop.png
   :width: 70%
   :align: center

-  Easy Gallery render

.. image:: https://github.com/dzhuang/django-gallery-widget/blob/main/demo/static/demo/screen_detail.png
   :width: 70%
   :align: center


What are the difference as compared to peer apps
-------------------------------------------------

-  `Django-files-widget <https://github.com/TND/django-files-widget>`__. In Django-files-widget, the files are managed and stored as ``string`` objects, which is actually the relative path of the files in the ``MEDIA_ROOT``. That means only a few user with granted permissions can upload/delete files uploaded to the server. In Django-Gallery-Widget, files are stored in ``imageField``, and it's possible to have better permission framework with regards to who can CRUD which images through views, and that expand the use case of the widget.

-  `Django-jfu <https://github.com/Alem/django-jfu>`__. It is a good demo of how to use Blueimp Jquery File Upload widget in Django. However, it currently only meet the demand of upload images via AJAX, not in terms of Gallery. And it has a long way for the demo to be integrated into an app, e.g., in terms of ``required``, ``readonly`` attribute of form fields.


Quick Start
-----------

Requirements
~~~~~~~~~~~~

-  Django 3.1 or later
-  `sorl-thumbnail <https://github.com/sorl/sorl-thumbnail>`__
-  `pillow <https://github.com/python-imaging/Pillow>`__ (or PIL)
-  npm and django-npm (for managing statics)
-  Bootstrap 3 or later (included)
-  jQuery 1.7 or later (included)
-  jQuery UI (included)
-  `blueimp/jQuery-File-Upload <https://github.com/blueimp/jQuery-File-Upload>`__
   (included)
-  `blueimp/Gallery <https://github.com/blueimp/Gallery>`__ (included)

Install
~~~~~~~

::

    pip install django-gallery-widget

Usage
~~~~~~~~~~~~~~~~~~

- In ``settings.py``, add 3 lines in you ``INSTALLED_APP``:

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'sorl.thumbnail',
        'gallery_widget',
        'demo',  # this line is required to run the demo
        ...,
    )

    DJANGO_GALLERY_CONFIG = ...

- If you want to use ``django-npm`` to manage the static dependencies, add the following lines in ``settings.py``:

.. code-block:: python

    from django.conf.global_settings import STATICFILES_FINDERS

    STATICFILES_FINDERS = tuple(STATICFILES_FINDERS) + (
        "npm.finders.NpmFinder",)


- in ``urls.py``, add the following line:

.. code-block:: python

    path(r"gallery-handler/", include("gallery_widget.urls")),


- Run the demo

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

.. note:: You might need to install JSON1 extension for SQLite for this the demo to run properly. See `Enabling JSON1 extension on SQLite <https://code.djangoproject.com/wiki/JSON1Extension>`__.

For advanced users
--------------------
Although the demo and built in image processing views might have meet the basic needs, advance user might require more
more in terms of permission control, template inheritance, and Image model customization.
Before that, we need to address the how this package is working.

Currently, Django don't have a `Field` which can store unknown length of images or
files. However, the introduction of ``JsonField`` (from Django 3) give us the possibility
to store the pks for image model instances (instances which has an ``ImageField``).

The first obstacle is we need to map the pks to the actual image models instances.
We finally work round this issue by saving the `app_label.model_name <https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.apps.get_model>`_
(which we called ``target_model`` thoughout the package) in the ``gallery_widget.fields.GalleryField``.

Following that, we need to have three basic views to handle image model instances, before saving their
pks to the ``GalleryField``: Create (which we called **upload**), List (which we called **fetch**) and Update
(which we mean **crop**).
The potential problems include: We will have to write 3 views each time we want to use a new ``target_model`` for
a new type of gallery/album, is there any shortcut that we don't need to write much code to achieve that?
And, can a gallery model field automatically know what default url name they should look for when trying to do the 3
tasks (find the views)? Our strategy is to introduce a class-based-view for each task, and
a default url name through adding a suffix to the model_name of the ``target_model``, and the last step
is mapping the url names and views function in the URL_CONF.


Therefore, a model level customization (for image model) involves:

A valid target image model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Image model is where we actually save the image instance uploaded. To be a valid target image model, it need to meet one of the following 2 requirements:

1. It has a ``django.db.models.ImageField`` named ``image``.

2. It has a ``django.db.models.ImageField`` which not named ``image``
   but the field can be accessed by a ``classmethod`` named ``get_image_field``.
   For example, in an app named ``my_app``, we can have the following valid target image model in
   ``my_app.models.py``:

.. code-block:: python

   class MyImage(models.Model):
        photo = models.ImageField(
            upload_to="my_images", storage=default_storage, verbose_name=_("Image"))
        creator = models.ForeignKey(
                settings.AUTH_USER_MODEL, null=False, blank=False,
                        verbose_name=_('Creator'), on_delete=models.CASCADE)
        creation_time = models.DateTimeField(default=now(), blank=False)

        @classmethod
        def get_image_field(cls):
            # Notice, we can't simply return 'cls.photo'
            return cls._meta.get_field("photo")

The ``gallery_widget.models.BuiltInGalleryImage`` is using the first style (with ``target_model="garllery_widget.BuiltInGalleryImage"``).
However, if you don't want to do much change to your existing models (e.g., avoiding migrations of existing model),
the second style is more sounding. In the following, we will use the above model in a ``GalleryField``
with ``target_model = "my_app.MyImage"``.


Three views for handling the image model objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Three views for handling the image model objects (upload, fetch and crop). We have provided 3
  class-based-views for these views to enable the built-in views.

  - ``gallery_widget.mixins.ImageCreateView``
  - ``gallery_widget.mixins.ImageListView``
  - ``gallery_widget.mixins.ImageCropView``

  We hope users can subclass the views above without much coding work. We think the `Built-in views
  <https://github.com/dzhuang/django-gallery-widget/blob/main/gallery_widget/views.py>`__
  set a good example of how to used them.

- URL_CONF configurations.
  A ``target_model`` should map the three different views above, to three url names in the `URL_CONF`.
  The default names are the lower cased model_name, suffixed by `-upload`, `-fetch` and `crop`,
  respectively. For example, if you have a `target_model` named ``my_app.MyImage``, then the default
  url names are ``myimage-upload``, ``myimage-fetch`` and ``myimage-crop``. In this way, you don't
  need to specify in the ``GalleryWidget`` the param ``upload_handler_url`` and ``fetch_request_url``,
  and no need to specify the ``crop_url_name`` in each of the 3 class based views.

Actually, most work the package has done is about image model instance manipulation.

Things that are simple
~~~~~~~~~~~~~~~~~~~~~~~
Here we finally come to the Gallery model part. There isn't much magic about how the GalleryField works, since
it is actually a JsonField. However, we need to first address the rendering the ``GalleryField``.
For example, with the ``MyImage`` in previous example as the ``target_model``, we now have a gallery model named ``MyGallery``:

.. code-block:: python

   class MyGallery(models.Model):
        album = GalleryField(target_model="my_app.MyImage", verbose_name=_('My photos'))
        owner = models.ForeignKey(
                settings.AUTH_USER_MODEL, null=False, blank=False,
                        verbose_name=_('Owner'), on_delete=models.CASCADE)


Then rendering the ``album`` can be as simple as (in Django CBS Listview)::

    {% for obj in object.album.objects.all %}
        <img src="{{ obj.photo.url}}">
    {% endfor %}

As you might guess from the first line, the ``GalleryField`` provide a ``Queryset`` API
for the image model instances it related to. No wonder, you can do the following::

   >>> first_gallery = MyGallery.objects.first()
   >>> photos_in_first_gallery = first_gallery.album.objects.all()
   >>> photos_before_2021 = photos_in_first_gallery.filter(creation_time__lt=datetime(2021, 01, 01))


More over, the demo provide a good example of `how to render <https://github.com/dzhuang/django-gallery-widget/blob/main/demo/templates/demo/demogallery_detail.html>`__
the field using ``sorl.thumbnail`` and ``Blueimp Gallery`` package.

Now it's your opportunity to show your skills on building various GREAT ASTONISHING AWESOME FANTASTIC gallery/album, which is beyond the scope of this package.

Settings
~~~~~~~~

Django Gallery Widget related settings is a dict as shown below. The default values can be seen at `gallery_widget.defaults <https://github.com/dzhuang/django-gallery-widget/blob/main/gallery_widget/defaults.py>`__ .

.. code-block:: python


    DJANGO_GALLERY_WIDGET_CONFIG = {
        "thumbnails": {
            "size": "120x80",
            "quality": 80
        },
        "jquery_file_upload_ui_options": { # options for jQuery-File-Upload
            ...
        },
        "assets": {
            "bootstrap.js": 'vendor/bootstrap/dist/js/bootstrap.min.js',
            "jquery.js": "vendor/jquery.min.js",
            ...
            "extra_js": [],
            "extra_css": [],
        },
        "widget_hidden_input_css_class": "django-gallery-widget",
        "prompt_alert_if_changed_on_window_reload": True,
    }

There's not much we might want to manipulate through the settings, besides thumbnail size
in the Image (upload/fetch/crop) UI. For ``jquery_file_upload_ui_options``,
please refer to `available options <https://github.com/blueimp/jQuery-File-Upload/wiki/Options#general-options>`__ for jQuery-File-Upload.

The ``widget_hidden_input_css_class`` option is the CSS class we wish to add to the hidden input field which save
the image pks. You might select another name, but we don't think it's necessary.

The ``prompt_alert_if_changed_on_window_reload`` is about whether an alert will be prompted by the browser when
user tries to navigate away or close the browser, while there're unsaved change in the page. Notice that feature is
not supported by Safari and some browser on IOS devices even if set to ``True`` (Not a bug).

.. warning::
   1. For ``jquery_file_upload_ui_options``, options ``fileInput``, ``paramName``, ``singleFileUploads``, ``previewMaxWidth`` and ``previewMaxHeight`` will
      be ignored (they were overridden in the package).

   2. This project relies heavily on CSS and JS frameworks/packages, so we strongly suggest using ``django-npm`` to manage the
      static assets. If you have other options, for example, not willing to have a local copy of those assets,
      you need to make sure ALL the items in `gallery_widget.defaults.DEFAULT_ASSET <https://github.com/dzhuang/django-gallery-widget/blob/c12a8f5328b558093f4aa423294698bdf460aa15/gallery_widget/defaults.py#L65>`__
      can be accessed properly. BTW, trying to ignore the commonly used framework such as Bootstrap (because you already has it in your instance) will
      result in failure in rendering the widget in Admin.


Credits
-------

-  `jQuery File
   Upload <https://github.com/blueimp/jQuery-File-Upload/wiki/Options>`__
-  `Django-files-widget <https://github.com/TND/django-files-widget>`__
   by Maarten ter Horst, which greatly inspired this project.
-  `Django-jfu <https://github.com/Alem/django-jfu>`__

This package can be views a Django package which tries to fully utilize `jQuery File Upload <https://github.com/blueimp/jQuery-File-Upload/wiki/Options>`__, with minimal customization.
Beside that, some of the ideas/code are inspired by `Django-jfu <https://github.com/Alem/django-jfu>`__ and `Django-files-widget <https://github.com/TND/django-files-widget>`__.



FAQs
-----
- Q: Why there isn't a delete view for image in the widget?

- A: Image upload behavior is much more complex than generic form views. Actually, the `jQuery File Upload <https://github.com/blueimp/jQuery-File-Upload/wiki/Options>`__ has a     working delete button, but we changed its behavior to just an UI behavior, considered the following situations:

  For a simpler case, when a user navigate away before saving the pks of the images they have just uploaded,
  it's almost impossible to delete those images from client side.

  Another situations happens when a gallery field is a required field. If there exists a delete view, when a user tries to delete ALL
  the images he/she had previously saved, from the ui, and then he/she submit the form. Undoubtedly, the form will raise an invalid error,
  and the gallery model won't be updated. However, since all the image instances has been deleted, the form will then display broken images
  after reloading.

  To avoid such situations, our suggestion is not to provide a delete view, but a strategy to identify orphan image model instances, and
  delete them with a cron task: trying to create an M2M connection between the image models and the gallery models.
  Through ``post-save`` signals of the gallery model, we are able to update the M2M relationship
  between all image model instance and related gallery model instances. In this way, image model instances which were not
  involved in any M2M relationship can be identified as what we called ``orphans``, the deletion of which are accurate and easy.


TODOs
-----

-  Detailed Documentation
-  More demos
-  Gif not client side croppable (don't show crop button)
-  Full tests
-  Scale large images in crop UI

Known issues
-------------

-  Currently, it's hard (although not impossible) to used the widget in a Non-model formfield.
-  Css rendering of buttons in Admin.
-  Gif will be converted to png (to retain gif, you need to set ``disableImageResize`` to ``False`` in ``jquery_fileupload_ui_options`` when initializing ``GalleryWidget``).
-  Doesn't support svg because django ImageField can't handle it for now.


License
-------------
Released under the `MIT license <https://opensource.org/licenses/MIT>`__.
