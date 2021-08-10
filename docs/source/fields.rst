GalleryField
---------------------

.. autoclass:: gallery_widget.fields.GalleryField
   :show-inheritance:


``GalleryField`` and ``GalleryImages``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: gallery_widget.fields

.. class:: GalleryImages

When you access a :class:`GalleryField` on a model, you are
given an instance of :class:`GalleryImages` as a proxy for accessing the
underlying images. Basically, a :class:`GalleryImages` instance
is a list of :attr:`pk` of the image model instances defined by
:attr:`target_model`. That means we can manipulate the field value with
method such as ``slice``, ``append()`` and ``extend()``.

For example::

   >>> g = Demogallery_widget.objects.first()
   >>> g.images
   [2, 1, 3]
   >>> len(g.images)
   3
   >>> g.images.append(4)  # assuming there is BuiltInGalleryImage with pk=4
   >>> g.save()
   >>> g.images
   >>> [2, 1, 3, 4]

Besides that, :class:`GalleryField` includes an :attr:`objects` attribute:

.. attribute:: GalleryImages.objects

An queryset of image instances.

That means we can do chained query to the attribute. Sample usage::

   >>> g.images.objects.all()
   <QuerySet [<BuiltInGalleryImage: BuiltInGalleryImage object (2)>, <BuiltInGalleryImage:
   BuiltInGalleryImage object (1)>, <BuiltInGalleryImage: BuiltInGalleryImage object (3)>,
   <BuiltInGalleryImage: BuiltInGalleryImage object (4)>]>
   >>> g.images.objects.filter(pk__lte=2)
   <QuerySet [<BuiltInGalleryImage: BuiltInGalleryImage object (2)>, <BuiltInGalleryImage:
   BuiltInGalleryImage object (1)>]>
   >>> g.images.objects.filter(pk__gte=5)
   <QuerySet []>

With the :attr:`objects` attribute, it's also handy to render images
contained in the field. For example, we use code like to the following snippet
in the template which renders detailed view of :class:`demo.models.DemoGallery`
instances:

.. code-block:: html

    {% for obj in object.images.objects.all %}
      <a href="{{ obj.image.url }}">
      </a>
    {% endfor %}

where ``object`` is an instance of :class:`demo.models.DemoGallery`.

GalleryFormField
---------------------

.. autoclass:: gallery_widget.fields.GalleryFormField
   :show-inheritance: