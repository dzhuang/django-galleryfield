Introduction
============

In this Django reusable app, we introduced a model field :class:`galleryfield.fields.GalleryField`,
a corresponding formfield :class:`galleryfield.fields.GalleryFormField` and the default
widget :class:`galleryfield.widgets.GalleryWidget`. The model field
makes it easy for image management at a collection level (i.e., a gallery or an album),
while the widget makes it easy to upload images via AJAX, allowing ordering the sequence arbitrarily,
and cropping images at both client and server side.

Features
**********

- A model field ``GalleryField``, and its formfield ``GalleryFormField`` along with the default
  widget ``GalleryWidget``.
- Drag & drop file uploading via AJAX
- Drag & drop ordering of images
- Uploading multiple images with progress bar
- Client / server side cropping (before/after upload).
- Integrates with Django Admin
- Admin user-proof, i.e., allowing non-staff user upload and manage gallery.


Motivation
**********

This package was created for some scenarios, where users were required to upload
multiple images by forms, and where the images can be **arbitrarily** ordered.

The original intended use case is: a type of assignment which requires students
to upload limited number of hand-written photos onto a Course Management Systems (CMS).
That requires:

-  Students can upload images through web UI (not via Admin) and preview instantly.
-  Students can order the uploaded images as they will, instead of ordering by upload time or file name.
-  Students can do some basic edit to images, like rotate and cropping.
-  There can be a restriction on the number of images, and the number differs between assignments.
-  The upload widget can be disabled (readonly), in this case, when deadline reaches.
-  Only the instructor and the student himself may do the CRUD of the images,
   with storage support, for example, via
   `django-sendfile2 <https://github.com/moggers87/django-sendfile2>`_.

For years, we've searched but failed to find Django apps which can meet all the requirements.


Limitations
***********

- The widget make it hard for image model instance to have extra attributes like
  ``title``, ``descriptions``, which limited the potential use case of the app.
  We were trying to find a way to enable adding/editing those attributes via the
  widget. Currently, the workaround I can think of is to introduce a foreign
  field to save the information of the images, and that require write more views
  by users.

- Compared to other Django apps, this app is relatively difficult to use, and it's
  not friendly for new developers in Django, in terms of customization.
  We've tried hard to design some class-based views to make that easier.

- Currently, no actual deletion of image model instance will be done through the web UI.
  With each image saved as an image model instance, user need to
  identify and delete the `orphaned` images instances (see our suggestion in :ref:`FAQ <faq>`).

- There's no direct way to add an image in a gallery to another gallery through the web
  UI, although the data models allow doing so.


Compared to peer apps
**********************

Just to name a few popular apps that have similar functionality with django-galleryfield.
Please correct me if I am wrong.

- `django-photologue <https://github.com/richardbarran/django-photologue>`_
   A popular app for managing photos and galleries, with built-in abstract models for
   photo objects, gallery and photo effects. The package
   requires images uploaded via admin, and multiple images need to be packed into a zip
   file before uploading. Besides, the images were sorted using
   `django-sortedm2m <https://github.com/jazzband/django-sortedm2m>`_, which means arbitrary
   sorting is impossible to implement without introducing extra fields.
   Those features make it hard to meet the demand of our use case.

- `django-files-widget <https://github.com/TND/django-files-widget>`_
   In this app, images/files are managed and stored as :class:`string` objects,
   which is actually the relative path of the files in the ``MEDIA_ROOT``.
   Moreover, its working logic need to conduct physical operations with image
   files, which make it impossible to store the files on storage like S3.

   In django-galleryfield, images are stored in :class:`django.db.models.ImageField`, which
   means we can store the images to various kind of storage
   (not just :class:`FileSystemStorage`).

- `django-jfu <https://github.com/Alem/django-jfu>`_
   A good demo on how to use ``blueimp/jQuery-File-Upload`` widget in Django. However,
   it only met the demand of upload images via AJAX, not in terms of Gallery, and there is
   a long way for the demo to be integrated into an app, e.g., in terms of ``required``,
   ``readonly`` attribute of form fields.

- `django-upload-form <https://github.com/morlandi/django-upload-form>`_
   It solved the problem of uploading multiple images from the frontend via a form.
   But the form is expecting to handling individual images, not the collection of images
   (gallery).

- `django-imaging <https://github.com/pielgrzym/django-imaging>`_
   It also introduced a new type of field called ``ImagingField``, however, it doesn't
   support more than one ``ImagingField`` per model.
