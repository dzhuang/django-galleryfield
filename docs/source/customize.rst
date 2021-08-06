Customize GalleryWidget
==============================

When talking about customize, there are different level of customization.


Model and views customization
---------------------------------


.. _customize-valid-image-model:

What is a valid target image model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to use an image model instead of the built-in one (i.e.,
:class:`gallery.models.BuiltInGalleryImage`), then you need to have a
`valid target image model` in the first place.

A valid target image model need to meet one of the following 2 requirements:

1. It has a :class:`django.db.models.ImageField` named ``image``

2. It has a :class:`django.db.models.ImageField` which not named ``image``
   but the field can be accessed by a `classmethod` :meth:`get_image_field`,
   for example:

.. code-block:: python

   class MyImage(models.Model):
        photo = models.ImageField(
            upload_to="my_images", storage=default_storage, verbose_name=_("Image"))
        creator = models.ForeignKey(
                settings.AUTH_USER_MODEL, null=False, blank=False,
                        verbose_name=_('Creator'), on_delete=models.CASCADE)

        @classmethod
        def get_image_field(cls):
            return cls._meta.get_field("photo")

.. note:: As demonstrated in above example, when defining the :meth:`get_image_field`,
   we can't simply ``return cls.photo`` because it
   returns a :class:`django.db.models.fields.files.ImageFieldFile`
   object instead of a :class:`django.db.models.ImageField` object.
