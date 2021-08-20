Introduction
============

In this Django reusable app, we introduced a model field :class:`gallery_widget.fields.GalleryField`
along with a corresponding formfield ``gallery_widget.fields.GalleryFormField`` and default
widget :class:`gallery_widget.widgets.GalleryWidget`. The model field
make it easy for image management at a collection level (i.e., what we called gallery or album),
while the widget make it easy to upload images via AJAX, allowing order the sequence arbitrarily,
and cropping images at both client and server side.

Features
**********

-  A model field ``GalleryField``, and its formfield ``GalleryFormField`` along with the default
   widget ``GalleryWidget``.
-  Drag & drop file uploading via AJAX
-  Uploading multiple images with progress bar
-  Drag & drop reordering
-  Client / server side cropping (before/after upload).
-  Integrates with Django Admin
-  Admin user-proof, i.e., allow non-staff user upload and manage gallery.


Motivation
**********

This package is created for some scenario, when users were required to upload
multiple images by a form. The images in the gallery can be arbitrarily
ordered, and can be cropped before or after uploaded.

For instance, students were required to upload limited number of hand-written photos on an
CMS platform as assignments. That requires:

-  Students can upload images through web UI (not Admin) and preview instantly.
-  Students can order the uploaded images as they will, instead of upload time or file name.
-  Students can do some basic edit to images, like rotate and cropping.
-  There can be a limit on the number of images, and the number differs between assignments.
-  Upload widget which can be disabled (readonly), in this case, when deadline reaches.
-  Only the instructor and the student himself may do the CRUD of the images,
   with storage support, for example,
   `django-sendfile2 <https://github.com/moggers87/django-sendfile2>`_.

For years, we've searched the open source software to look for Django apps, but failed to meet
all the requirements.


Limitations
***********

- The widget make it hard for image model instance to have attributes like ``title``,
  ``descriptions``, which limited the potential use case of the app.
  We planed to make those attribute possible in future release. The work around might
  be introduce a foreign field to save the information of the images, and that require
  write more views by users.

- Kind of hard to use, for fresh developers in django, in terms of customization.
  We've tried hard to design some class-based views to make that easier.

- Currently, no actual delete of image model instance will be done through the web UI.
  However, as each image saved as an image model instance, we propose a workaround
  strategy to identify and delete the `orphan` images instances (see in FAQ).

- There's no direct way to add an image in a gallery to another gallery through the web
  UI, although the data models allow doing so.


Compared to peer apps
**********************

Just name a few popular apps that have similar functionality with django-gallery-widget.
Please correct me if I am wrong.

- `django-photologue <https://github.com/richardbarran/django-photologue>`_
   A popular app for managing photos and galleries, with built-in abstract models for
   photo objects, gallery and photo effects. The package
   requires images uploaded via admin, and multiple images need to be packed into a zip
   file before upload. Besides, the images were sorted using
   `django-sortedm2m <https://github.com/jazzband/django-sortedm2m>`_, which means arbitrary
   sorting is impossible to implement without introducing more fields.
   Those features make it hard to meed the demand of our use case.

- `django-files-widget <https://github.com/TND/django-files-widget>`_
   In this app, images/files are managed and stored as :class:`string` objects,
   which is actually the relative path of the files in the ``MEDIA_ROOT``. That means only a
   few user with granted permissions can upload/delete files uploaded to the server. More
   over, its working logic need a lot of physical interaction with image files, which make
   it impossible to store the files on storage like S3.

   In django-gallery-widget, images are stored in ``imageField`` of image models,
   and it's possible to have better permission management with regards to who can
   CRUD which images through views, and that expand the use case of the widget.

- `django-jfu <https://github.com/Alem/django-jfu>`_
   A good demo on how to use Blueimp Jquery File Upload widget in Django. However,
   it currently only meet the demand of upload images via AJAX, not in terms of Gallery.
   And it has a long way for the demo to be integrated into an app, e.g., in terms of ``required``,
   ``readonly`` attribute of form fields.

- `django-upload-form <https://github.com/morlandi/django-upload-form>`_
   It solved the
   problem of uploading multiple images from the frontend via a form.
   But the form is handling images, not the collection of images.
