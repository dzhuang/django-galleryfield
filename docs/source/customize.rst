Customize my GalleryWidget
==============================

When talking about customize, there are different level of customization.


Model and view customization
---------------------------------


.. _customize-valid-image-model:

What is a valid target image model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A string in the form of ``"app_label.model_name"``, which can be loaded by
:meth:`django.apps.get_model` (see
`Django docs <https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.apps.get_model>`_),
defaults to ``None``. If `None`, ``gallery.BuiltInGalleryImage``,
which can be overridden by
``settings.DJANGO_GALLERY_WIDGET_CONFIG["default_target_image_model"]``,
will be used.

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

