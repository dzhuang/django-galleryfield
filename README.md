Django-Gallery-Widget
===================

[![codecov](https://codecov.io/gh/dzhuang/django-gallery-widget/branch/main/graph/badge.svg)](https://codecov.io/gh/dzhuang/django-gallery-widget)

Django AJAX form widgets and model fields for multiple images upload with progress bar.
Some of the ideas/code are inspired by [Django-jfu](https://github.com/Alem/django-jfu) and 
[Django-files-widget](https://github.com/TND/django-files-widget).

__This is currently an alpha release.__

Features
--------

- Drag &amp; drop file uploading via AJAX
- Uploading multiple images with progress bar
- A model fields with corresponding form fields and widgets: `gallery.fields.GalleryField`
- Image gallery widget with drag &amp; drop reordering, client side crop before/after upload.
- Integrates with Django Admin.


ScreenShots
-----------
- Multiple image upload, sortable

  <img class="img-responsive" src="https://github.com/dzhuang/django-gallery-widget/raw/main/demo/static/demo/screen_upload.png" width="70%">

- Client/Server side crop
  
  <img class="img-responsive" src="https://github.com/dzhuang/django-gallery-widget/raw/main/demo/static/demo/screen_crop.png" width="70%">

- Easy Gallery render

  <img class="img-responsive" src="https://github.com/dzhuang/django-gallery-widget/raw/main/demo/static/demo/screen_detail.png" width="70%">

Quick Start
-----------

### Requirements ###

- Django 3.2 or later
- [sorl-thumbnail](https://github.com/sorl/sorl-thumbnail)
- [pillow](https://github.com/python-imaging/Pillow) (or PIL)
- Bootstrap 3 or later (included)
- jQuery 1.7 or later (included)
- jQuery UI (included)
- [blueimp/jQuery-File-Upload](https://github.com/blueimp/jQuery-File-Upload) (included)
- [blueimp/Gallery](https://github.com/blueimp/Gallery) (included)


### Install ###

    pip install git+git://github.com/dzhuang/django-gallery-widget.git

### In `settings.py` ###

    INSTALLED_APPS = (
        ...,
        'sorl.thumbnail',
        'gallery',
        ...,
    )
    
    DJANGO_GALLERY_CONFIG = ...
    
    
### In `urls.py` ###

    path(r"gallery-handler/", include("gallery.urls")),


### Run the demo ###
    git clone https://github.com/dzhuang/django-gallery-widget.git
    cd django-gallery-widget
    cd demo
    pip install -r requirements.txt
    cd ..
    python manage.py migrate
    python manage.py createsuperuser # Create a superuser account so that you can upload images
    python manage.py runserver

Then in your browser navigate to http://127.0.0.1:8000/admin and login, then return to http://127.0.0.1:8000/.

**Notice**: You might need to install JSON1 extension for SQLite for this the demo to run
properly. See [Enabling JSON1 extension on SQLite](https://code.djangoproject.com/wiki/JSON1Extension).

License
-------

MIT

Credits
-------

- [jQuery File Upload](https://github.com/blueimp/jQuery-File-Upload/wiki/Options)
- [Django-files-widget](https://github.com/TND/django-files-widget) by Maarten ter Horst, which greatly inspired this project.
- [Django-jfu](https://github.com/Alem/django-jfu)


Navigation
----------

### Settings
Django Gallery Widget related settings is a dict as shown below with default value.   

```Python

DJANGO_GALLERY_WIDGET_CONFIG = {
    "default_urls":
        {"upload_handler_url_name": "gallery_image_upload",
         "fetch_url_name": "gallery_images_fetch",
         "crop_url_name": "gallery_image_crop"},
    "default_target_image_model": "gallery.BuiltInGalleryImage",
    "assets": {
        "bootstrap_js_path": 'vendor/bootstrap/dist/js/bootstrap.min.js',
        "bootstrap_css_path": "vendor/bootstrap/dist/css/bootstrap.min.css",
        "jquery_js_path": "vendor/jquery.min.js",
        "extra_js": [],
        "extra_css": [],
    },
    "thumbnails": {
        "size": 120,
        "quality": 80
    },
    "widget_hidden_input_css_class": "django-gallery-widget",
    "prompt_alert_if_changed_on_window_reload": True,
}

```
#### Model related default_values
Django-Gallery-Widget has a built-in image Model `gallery.models.BuiltInGalleryImage`,
 in which `image` is the target field of the gallery model. User can use this models 
 without much modifying in their apps. See the demo app for details. With that built-in model,
 default views are applied with default urls (i.e, `upload_handler_url_name`, `fetch_url_name` 
 and `crop_url_name`).

However, it is heavily suggested for developers to write your own image models, views, urls,
and override those settings for your apps, especially in terms of permission considerations.

### What are the difference as compared to peer apps
- [Django-files-widget](https://github.com/TND/django-files-widget)

  In Django-files-widget, the files are managed and stored as `string` objects, which is actually the relative
  path of the files in the `MEDIA_ROOT`. That means only a few user with granted permissions
  can upload/delete files uploaded to the server. In Django-Gallery-Widget, files are
  stored in `imageField`, and it's possible to have better permission framework with
  regards to who can CRUD which images through views, and that expand the use case
  of the widget.

- [Django-jfu](https://github.com/Alem/django-jfu)
  
  It is a good demo of how to use Blueimp Jquery File Upload widget in Django. However, it 
  currently only meet the demand of upload images via AJAX, not in terms of Gallery. And it has
  a long way for the demo to be integrated into an app, e.g., in terms of `required`, `readonly` attribute
  of form fields.

## TODOs
- Detailed Documentation
- More demos
- Descriptors for rendering the `GalleryField`.

## Known issues
- Css rendering of buttons in Admin.
