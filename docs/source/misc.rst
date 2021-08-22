Credits
===============

-  `jQuery File
   Upload <https://github.com/blueimp/jQuery-File-Upload/wiki/Options>`_
-  `django-files-widget <https://github.com/TND/django-files-widget>`_
   by Maarten ter Horst, which greatly inspired this project.
-  `django-jfu <https://github.com/Alem/django-jfu>`_
-  `Cropper <https://fengyuanchen.github.io/cropper>`_ by Chen Fengyuan.

This package can be views a Django package which tries to fully utilize `jQuery File Upload <https://github.com/blueimp/jQuery-File-Upload/wiki/Options>`_, with minimal customization.
Beside that, some of the ideas/code are inspired by `Django-jfu <https://github.com/Alem/django-jfu>`_ and `Django-files-widget <https://github.com/TND/django-files-widget>`_.



FAQs
===============
- Q: Why there isn't a delete view for image in the widget?

- A: Image upload behavior is much more complex than generic form views. Actually, the `jQuery File Upload <https://github.com/blueimp/jQuery-File-Upload/wiki/Options>`__ has a     working delete button, but we changed its behavior to just an UI behavior, considered the following situations:

  For a simpler case, when a user navigate away before saving the pks of the images they have just uploaded,
  it's almost impossible to delete those images from client side.

  Another situations happens when a gallery field is a required field. If there exists a delete view, when a user tries to delete ALL
  the images he/she had previously saved, from the ui, and then he/she submit the form. Undoubtedly, the form will raise an invalid error,
  and the gallery model won't be updated. However, since all the image instances has been deleted, the form will then display broken images
  after reloading.

  To avoid such situations, our suggestion is not to provide a delete view, but a strategy to identify orphan image model instances, and
  delete them with a cron task: trying to create an M2M connection between the image models and the gallery models.
  Through ``post-save`` signals of the gallery model, we are able to update the M2M relationship
  between all image model instance and related gallery model instances. In this way, image model instances which were not
  involved in any M2M relationship can be identified as what we called ``orphans``, the deletion of which are accurate and easy.


TODOs
===============

-  Detailed Documentation
-  More demos
-  Gif not client side croppable (don't show crop button)
-  Full tests
-  Scale large images in crop UI

Known issues
===============

-  Currently, it's hard (although not impossible) to used the widget in a Non-model formfield.
-  Css rendering of buttons in Admin.
-  Gif will be converted to png (to retain gif, you need to set ``disableImageResize`` to ``False`` in ``jquery_fileupload_ui_options`` when initializing ``GalleryWidget``).
-  Doesn't support svg because django ImageField can't handle it for now.


License
===============
Released under the `MIT license <https://opensource.org/licenses/MIT>`__.