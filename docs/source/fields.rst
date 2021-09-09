Model field and form field
===================================

GalleryField
-------------

.. autoclass:: galleryfield.fields.GalleryField
   :show-inheritance:


``GalleryField`` and ``GalleryImages``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: galleryfield.fields

.. class:: GalleryImages

When you access a :class:`GalleryField` on a model, you are
given an instance of :class:`GalleryImages` as a proxy for accessing the
underlying images. Basically, a :class:`GalleryImages` instance
is a list of :attr:`pk` of the image model instances defined by
:attr:`target_model`. That means we can manipulate the field value with
method such as ``slice``, ``append()`` and ``extend()``.

For example::

   >>> g = Demogallery.objects.first()
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
contained in the field. For example, we can use following snippet
in the template to detailed view of :class:`demo.models.DemoGallery`
instances:

.. code-block:: html

    {% for obj in object.images.objects.all %}
      <a href="{{ obj.image.url }}">
      </a>
    {% endfor %}

where ``object`` in the first line is an instance of :class:`demo.models.DemoGallery`.

GalleryFormField
---------------------

.. autoclass:: galleryfield.fields.GalleryFormField
   :show-inheritance:

.. note:: :class:`galleryfield.fields.GalleryFormField` is not supposed to be used independently
   (i.e., as a non-modelform field). The most possible cases for us to access the formfield are
   in the modelform configurations. For example:

    .. code-block:: python

        class MyGalleryForm(forms.ModelForm):
            class Meta:
                model = MyGallery
                fields = ["images"]

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.fields["images"].required = False
                self.fields["images"].max_number_of_images = 2

                # from django.forms.widgets import Textarea
                # self.fields["images"].widget = Textarea()  # Use Textarea as widget


.. warning:: If you want to use :class:`galleryfield.fields.GalleryFormField` as a non-modelform
   field, remember to initialize the
   field with a key word argument like ``target_model="my_app.MyImage"``, otherwise it will use
   ``galleryfield.BuiltInGalleryImage`` as the ``target_model``. Also, keep in mind that
   the ``cleaned_data`` of the field only contains the ``pk`` of the image model instances.
