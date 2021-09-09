Customization
===============

Although the built-in image model, along with the image processing views
demonstrated in the demo, might have met the basic needs for some apps,
advance users might require more features in terms of image storage,
permission control, template inheritance, and Image model (fields)
customization.

Before that, we need to address how this app is working.

Image model and views
----------------------

Until now, Django didn't supply any type of `Field` which can store unknown
length of images or files. However, the introduction of :class:`JsonField`
(in Django 3) made it possible to store the ``pks``
of image model instances as a Json list in a customized :class:`JsonField`.
That's the :class:`galleryfield.fields.GalleryField`.

To facilitate the access of image model instances, we need to map the ``pks``
to the actual image model instances. So, we introduced an optional :class:`string`
param ``target_model``, the
`app_label.model_name <https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.apps.get_model>`_
of the image model, defaults to ``garlleryfield.BuiltInGalleryImage``.

Following that, there should be three basic views to handle image model instances:
Create (the **upload** operation), List (the **fetch** operation)
and Update (the **crop** operation).

The next problem is, when customizing, image models varies because
they can have more fields besides an :class:`ImageField` and an :class:`User` field,
e.g., a :class:`DatetimeField` to store the upload time of the image.
And, we will never being able to know how other developers will name those fields.
Inevitably, developers will have to write those 3 views for their ``target_models``.
Moreover, the widget should be able to know where to find those views, i.e.,
it need to know the URLs of those views.

To solve the problems, We finally introduced a class-based views for
each operation, and specified a :ref:`naming rule <image_handling_url_naming_rule>`
for the URL names of the 3 views for a ``target_model``.

Therefore, a model level customization (for image model) involves:


.. _customize-valid-image-model:

A valid target image model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Image model is where we actually save the image uploaded. To be a valid target image model,
it need to meet one of the following 2 requirements:

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

.. note:: In the example above, when defining the :meth:`get_image_field`,
   we can't simply ``return cls.photo`` because it
   returns a :class:`django.db.models.fields.files.ImageFieldFile`
   object instead of a :class:`django.db.models.ImageField` object.

The :class:`galleryfield.models.BuiltInGalleryImage` is using the first style (
with ``target_model="garlleryfield.BuiltInGalleryImage"``).
However, if you don't want to do much change to your existing models
(e.g., avoiding migrations of existing model),
the second style is more sounding.

In the following, we will use the above model in a :class:`galleryfield.fields.GalleryField`
with ``target_model = "my_app.MyImage"``.


Three views for handling the image model objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Three views for handling the image model objects (upload, fetch and crop). We provided 3
  class-based-views for these views to enable the built-in views.

  - :class:`galleryfield.image_views.ImageCreateView`
  - :class:`galleryfield.image_views.ImageListView`
  - :class:`galleryfield.image_views.ImageCropView`

  See :ref:`Built-in Image handling Views <built-in-image-views>` for more detail. We hope users can subclass
  the views above without much coding work. We think the 3 views
  handling built-in image model (i.e., :class:`galleryfield.image_views.BuiltInImageCreateView`,
  :class:`galleryfield.image_views.BuiltInImageListView` and
  :class:`galleryfield.image_views.BuiltInImageCropView` were good examples of how to used them.


.. _image_handling_url_naming_rule:

Naming rule for URLs of image handling views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generally, the widget need to know the URLs for image handling views (see :ref:`GalleryWidget docs <widget_docs>`).
We may specify the explicitly specify the URL names manually in the widget of gallery modelform
fields.

Alternatively, we can also let the widget infer what URLs it should use for those views, by
following a naming rules for those views in ``URL_CONF``.

For a valid image model, the default URL names for the image handling views are the lower cased
``app_label-model_name``, suffixed by ``-upload``, ``-fetch`` and ``-crop``,
respectively.

For example, if you have a ``target_model`` named ``my_app.MyImage``, then the default
URL names for the image handling views are ``my_app-myimage-upload``, ``my_app-myimage-fetch`` and
``my_app-myimage-crop``. In this way, you don't need to specify in the ``GalleryWidget``
the param ``upload_url`` and ``fetch_url``, and no need to specify the ``crop_url_name``
in each of the 3 class-based views.

Until now, we were talking about image model instance handling.


GalleryField rendering customization
--------------------------------------

Now we turn to the customization of gallery model.
Back to the demo, when dealing with the gallery model instance, there isn't much magic about
:class:`demo.views.GalleryCreateView` and :class:`demo.views.GalleryUpdateView`.
Here, we need to address :class:`demo.views.GalleryDetailView`, on how it renders the
:class:`galleryfield.fields.GalleryField`.

With ``my_app.MyImage`` in previous example as the ``target_model``,
we can have a gallery model named ``MyGallery``:

.. snippet:: python
   :filename: my_app/models.py

   class MyGallery(models.Model):
        album = GalleryField(target_model="my_app.MyImage", verbose_name=_('My photos'))
        owner = models.ForeignKey(
                settings.AUTH_USER_MODEL, null=False, blank=False,
                        verbose_name=_('Owner'), on_delete=models.CASCADE)


By subclassing :class:`django.views.generic.detail.DetailView`, we can have a gallery detail view like:

.. snippet:: python
   :filename: my_app/views.py

    from django.views.generic.detail import DetailView
    from my_app.models import MyGallery

    class MyGalleryDetailView(DetailView):
        model = MyGallery

Then we add a template file named ``mygallery_detail.html`` to folder ``my_app/templates/my_app/``,
with the following code block:

.. snippet:: html
   :filename: my_app/templates/my_app/mygallery_detail.html

    {% extends 'base.html' %}
    {% load static %}

    ...

    {% for obj in object.album.objects.all %}
        <img src="{{ obj.photo.url}}">
    {% endfor %}

    ...


And add the URL of the view:

.. snippet:: python
   :filename: my_app/urls.py

    from my_apps import views

    urlpatterns = [
        ...
        path('album-detail/<int:pk>',
             views.MyGalleryDetailView.as_view(), name='my_gallery-detail'),
    ]

Then we can navigate to see the images in a specific gallery.

As you might guess from the first line in the template snippet,
the ``GalleryField`` provide a ``Queryset`` API for the image model
instances it related to. No wonder, you can do the following::

   >>> first_gallery = MyGallery.objects.first()
   >>> photos_in_first_gallery = first_gallery.album.objects.all()
   >>> photos_before_2021 = photos_in_first_gallery.filter(creation_time__lt=datetime(2021, 01, 01))


More over, the demo provides an  example of `how to render <https://github.com/dzhuang/django-galleryfield/blob/main/demo/templates/demo/demogallery_detail.html>`__
the field using ``sorl.thumbnail`` and ``Blueimp Gallery`` package.

Finally, it's your opportunity to show your skills on customizing the gallery/album frontend, which is beyond the scope of this package.


Template customization
-------------------------------
TODO
