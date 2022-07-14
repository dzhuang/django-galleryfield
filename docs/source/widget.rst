GalleryWidget
===============

.. _widget_docs:

The ``GalleryWidget`` class
----------------------------

.. autoclass:: galleryfield.widgets.GalleryWidget

.. note:: When a :class:`galleryfield.fields.GalleryField` instance is initialized
   with ``galleryfield.BuiltInGalleryImage``, the widget instance will
   automatically use URL names ``galleryfield-builtingalleryimage-upload``
   ``galleryfield-builtingalleryimage-fetch`` for :attr:`upload_url`, :attr:`fetch_url`,
   respectively.

The URL params can be overridden after the form is instantiated. For example:

.. snippet:: python
   :filename: my_app/forms.py

    from my_app.models import MyGallery

    class MyGalleryForm(forms.ModelForm):
        class Meta:
            model = MyGallery
            fields = ["album"]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["album"].widget.upload_url = "/path/to/my-upload-handler"

The validity of the URL params will be checked before rendering.

.. warning:: You NEED to make sure all the urls in the widget are
   handling the corresponding :attr:`target_model` before put into
   production. As a minimal precaution,
   when a :class:`galleryfield.fields.GalleryField` instance (
   or a :class:`galleryfield.fields.GalleryFormField` instance, or image handling views
   ) is
   **NOT** initialized with ``galleryfield.BuiltInGalleryImage`` as the
   :attr:`target_model`, assigning built-in URL names (
   i.e., ``galleryfield-builtingalleryimage-upload``, ``galleryfield-builtingalleryimage-fetch``)
   in widget params, or set ``galleryfield-builtingalleryimage-crop`` for `crop_url_name` in
   image handling views, :exc:`ImproperlyConfigured` will be raised
   when rendering. The reason is, those built-in views are handling
   built-in :class:`galleryfield.models.BuiltInGalleryImage` instances.
