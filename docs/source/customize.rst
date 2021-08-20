Customization
===============

Although the demo and built in image processing views might have meet the basic needs, advance user might
require more in terms of image storage, permission control, template inheritance, and Image model field
customization. Before that, we need to address how this package is working.

Model and views
------------------

Currently, Django don't have a `Field` which can store unknown length of images or
files. However, the introduction of ``JsonField`` (from Django 3) give us the possibility
to store the pks for image model instances (instances which has an ``ImageField``).

The first obstacle is we need to map the pks to the actual image models instances.
We finally work round this issue by saving the `app_label.model_name <https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.apps.get_model>`_
(which we called ``target_model`` throughout the package) in :class:`gallery_widget.fields.GalleryField`.

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


.. _customize-valid-image-model:

A valid target image model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Image model is where we actually save the image instance uploaded. To be a valid target image model, it need to meet one of the following 2 requirements:

1. It has a ``django.db.models.ImageField`` named ``image``.

2. It has a ``django.db.models.ImageField`` which not named ``image``
   but the field can be accessed by a ``classmethod`` named ``get_image_field``.
   For example, in an app named ``my_app``, we can have the following valid target image model in
   ``my_app.models.py``:

.. snippet:: python
   :filename: my_app/models.py

   class MyImage(models.Model):
        photo = models.ImageField(
            upload_to="my_images", storage=default_storage, verbose_name=_("Image"))
        creator = models.ForeignKey(
                settings.AUTH_USER_MODEL, null=False, blank=False,
                        verbose_name=_('Creator'), on_delete=models.CASCADE)
        creation_time = models.DateTimeField(default=now(), blank=False)

        @classmethod
        def get_image_field(cls):
            return cls._meta.get_field("photo")

.. note:: As demonstrated in above example, when defining the :meth:`get_image_field`,
   we can't simply ``return cls.photo`` because it
   returns a :class:`django.db.models.fields.files.ImageFieldFile`
   object instead of a :class:`django.db.models.ImageField` object.

The :class:`gallery_widget.models.BuiltInGalleryImage` is using the first style (
with ``target_model="garllery_widget.BuiltInGalleryImage"``).
However, if you don't want to do much change to your existing models (e.g., avoiding migrations of existing model),
the second style is more sounding. In the following, we will use the above model in a :class:`gallery_widget.fields.GalleryField`
with ``target_model = "my_app.MyImage"``.


Three views for handling the image model objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Three views for handling the image model objects (upload, fetch and crop). We provided 3
  class-based-views for these views to enable the built-in views.

  - :class:`gallery_widget.views.ImageCreateView`
  - :class:`gallery_widget.views.ImageListView`
  - :class:`gallery_widget.views.ImageCropView`

  See :ref:`Built-in Image handling Views <built-in-image-views>` for more detail. We hope users can subclass the views above without much coding work. We think the 3 views
  handling built-in image model (i.e., :class:`gallery_widget.views.BuiltInImageCreateView`,
  :class:`gallery_widget.views.BuiltInImageListView` and
  :class:`gallery_widget.views.BuiltInImageCropView` were good examples of how to used them.


.. _image_handling_url_naming_rule:

Naming rule for image handling views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generally, the widget need to know the urls for image handling views (see :ref:`GalleryWidget docs <widget_docs>`).
We may specify the url name manually in gallery modelform fields widget configurations.
Alternatively, we can also let the widget infer what urls it should use for those views, by
following a naming rules for those views in `URL_CONF`.
The default url names are the lower cased model_name, suffixed by ``-upload``, ``-fetch`` and ``-crop``,
respectively. For example, if you have a `target_model` named ``my_app.MyImage``, then the default
url names are ``myimage-upload``, ``myimage-fetch`` and ``myimage-crop``. In this way, you don't
need to specify in the ``GalleryWidget`` the param ``upload_handler_url`` and ``fetch_request_url``,
and no need to specify the ``crop_url_name`` in each of the 3 class based views.

Until now, we were talking about image model instance handling.


GalleryField rendering customization
--------------------------------------

Back to the demo, when dealing with the gallery model instance, there isn't much magic about
:class:`demo.views.GalleryCreateView` and :class:`demo.views.GalleryUpdateView`.
Here, we need to address :class:`demo.views.GalleryDetailView`, on how it rendering the ``GalleryField``.

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


More over, the demo provide an  example of `how to render <https://github.com/dzhuang/django-gallery-widget/blob/main/demo/templates/demo/demogallery_detail.html>`__
the field using ``sorl.thumbnail`` and ``Blueimp Gallery`` package.

Now it's your opportunity to show your skills on customizing the gallery/album frontend, which is beyond the scope of this package.


Template customization
-------------------------------
TODO
