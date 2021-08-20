Behind the demo
================

The code in the demo seems very simple, with only a model field :class:`gallery_widget.fields.GalleryField`
imported in ``demo.models`` to construct the gallery model. However, there're some logic falls behind the
code.

How it handles the images
--------------------------

The demo is actually using built-in :class:`gallery_widget.models.BuiltInGalleryImage`, which has 2
fields (a :class:`gallery_widget.fields.GalleryField` named ``image`` and a ``User`` field named ``creator``),
to store the uploaded images.

Further, If you look into ``gallery_widget.urls`` and ``gallery_widget.views``,
you will see 3 class-based views:

- :class:`gallery_widget.views.BuiltInImageCreateView` for uploading images,
  requires login.
  Following the :ref:`naming rule <image_handling_url_naming_rule>`, The url name is ``builtingalleryimage-upload``.
- :class:`gallery_widget.views.BuiltInImageListView` for fetching existing images,
  restricted to the owner of the images or superuser.
  The url name is ``builtingalleryimage-fetch``.
- and :class:`gallery_widget.views.BuiltInImageCropView` for server side cropping
  of uploaded images, restricted to the owner of the images or superuser.
  The url name is ``builtingalleryimage-crop``


How it handles the gallery
---------------------------

The handling of galleries is fairly simple as compared to images. The views are provided

- :class:`demo.views.GalleryCreateView` is used to create new gallery, restricted to owner and superuser.
- :class:`demo.views.GalleryUpdateView` is used to update existing gallery (add/delete/crop images), restricted to owner and superuser.
- and :class:`demo.views.GalleryDetailView` is used to render the gallery, requires no authentication.
