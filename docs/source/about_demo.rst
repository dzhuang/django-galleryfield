About the demo
================

The code in the demo seems simple, with only a model field :class:`galleryfield.fields.GalleryField`
used in ``demo.models`` to construct the gallery model. Actually, there are some logic fall behind the
code.

Handling the image instances
-----------------------------

Although we didn't explicitly specify in the code, the demo is actually using
built-in :class:`galleryfield.models.BuiltInGalleryImage` as the image model for
creating, listing, and updating images.
The image model has 2 fields: a :class:`galleryfield.fields.GalleryField` named ``image``
and an ``User`` field named ``creator``. We think whatever it called, an ``User``
field is needed because that's the basis for the server to determine the
whether requested users are qualified to modify the image instances, or to view the
image instances in a form listview,  or to potentially delete existing
image instances.

Further, If you look into ``galleryfield.urls`` and ``galleryfield.image_views``,
you will see 3 class-based views which are handling images (or image instances):

- :class:`galleryfield.image_views.BuiltInImageCreateView` for uploading images,
  requires login.
  Following the :ref:`naming rule <image_handling_url_naming_rule>`, The URL name is
  ``galleryfield-builtingalleryimage-upload``.
- :class:`galleryfield.image_views.BuiltInImageListView` for fetching existing images,
  restricted to the owner of the images or superuser, with URL name
  ``galleryfield-builtingalleryimage-fetch``.
- and :class:`galleryfield.image_views.BuiltInImageCropView` for server side cropping
  of uploaded images, restricted to the owner of the images or superuser, with URL
  name ``galleryfield-builtingalleryimage-crop``.


Handling the gallery
---------------------------

In ``demo.models``, we defined a gallery model named :class:`DemoGallery`, which contains
a :class:`galleryfield.fields.GalleryField` named ``images``, and again an ``User`` field named
``owner`` which is also used to guarantee permissions of requested user to create and update
gallery instances.

The handling of galleries is fairly simple as compared to images. The views for galleries
were in ``demo.views`` and its ``URL_CONF`` were in ``demo.urls``. Three views were provided:

- :class:`demo.views.GalleryCreateView` is responsible for creating new gallery instances, restricted to owner and superuser.
- :class:`demo.views.GalleryUpdateView` is responsible for updating existing gallery instances (add/delete/order images), restricted to owner and superuser.
- and :class:`demo.views.GalleryDetailView`, which is responsible for rendering the gallery, requires no authentication.
