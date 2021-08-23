Image handling views
=====================

.. _built-in-image-views:

Base image handling Views
------------------------------

If not disabled, each image model need to have 3 views for uploading, fetching and cropping.
User should subclass the following Class-based image handling base views for your custom image models.

.. |view_target_model| replace::

    When not set, defaults to ``garllery_widget.BuiltInGalleryImage``


.. |view_crop_url_name| replace::

    When :attr:`disable_server_side_crop` is False, if ``None`` or
    an invalid URL name will raise an :exc:`ImproperlyConfigured` error.

.. |view_disable_server_side_crop| replace::

    Defaults to ``False``


.. autoclass:: galleryfield.image_views.ImageCreateView
.. autoclass:: galleryfield.image_views.ImageListView
.. autoclass:: galleryfield.image_views.ImageCropView
