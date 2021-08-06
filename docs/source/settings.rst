========
Settings
========

.. contents::
    :local:
    :depth: 1

.. setting:: DJANGO_GALLERY_WIDGET_CONFIG

``DJANGO_GALLERY_WIDGET_CONFIG``
---------------------------------

Default::

    {
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

.. setting:: default_target_image_model

assets
~~~~~~~

Default::

    {
        "bootstrap_js_path": 'vendor/bootstrap/dist/js/bootstrap.min.js',
        "bootstrap_css_path": "vendor/bootstrap/dist/css/bootstrap.min.css",
        "jquery_js_path": "vendor/jquery.min.js",
        "extra_js": [],
        "extra_css": []
    }


Allow single or part overriding. The paths can be URLs, CDN address or local paths, see
`configuring-static-files <https://docs.djangoproject.com/en/3.2/howto/static-files/#configuring-static-files>`_
for reference. ``extra_js`` and ``extra_css`` are useful when you want add extra JS or CSS
when inheriting :template:`gallery/widget.html`.


The ``integrity`` and ``crossorigin`` were unable to be configured except hard coding

.. setting:: default_urls

``default_urls``
~~~~~~~~~~~~~~~~~

Default::

    {
        "upload_handler_url_name": "gallery_image_upload",
         "fetch_url_name": "gallery_images_fetch",
         "crop_url_name": "gallery_image_crop"
    }

A dictionary which contains all the default URL names which will be used by
the :class:`gallery.widgets.GalleryWidget` instance when not specified.



.. setting:: ADMINS

``ADMINS``
----------

Default: ``[]`` (Empty list)

A list of all the people who get code error notifications. When
:setting:`DEBUG=False <DEBUG>` and :class:`~django.utils.log.AdminEmailHandler`
is configured in :setting:`LOGGING` (done by default), Django emails these
people the details of exceptions raised in the request/response cycle.

Each item in the list should be a tuple of (Full name, email address). Example::



    [('John', 'john@example.com'), ('Mary', 'mary@example.com')]

.. setting:: ALLOWED_HOSTS

``ALLOWED_HOSTS``
-----------------

Default: ``[]`` (Empty list)


Values in this list can be fully qualified names (e.g. ``'www.example.com'``),
in which case they will be matched against the request's ``Host`` header
exactly (case-insensitive, not including port). A value beginning with a period
can be used as a subdomain wildcard: ``'.example.com'`` will match
``example.com``, ``www.example.com``, and any other subdomain of
``example.com``. A value of ``'*'`` will match anything; in this case you are
responsible to provide your own validation of the ``Host`` header (perhaps in a
middleware; if so this middleware must be listed first in
:setting:`MIDDLEWARE`).

Django also allows the `fully qualified domain name (FQDN)`_ of any entries.
Some browsers include a trailing dot in the ``Host`` header which Django
strips when performing host validation.

.. _`fully qualified domain name (FQDN)`: https://en.wikipedia.org/wiki/Fully_qualified_domain_name

If the ``Host`` header (or ``X-Forwarded-Host`` if
:setting:`USE_X_FORWARDED_HOST` is enabled) does not match any value in this
list, the :meth:`django.http.HttpRequest.get_host()` method will raise
:exc:`~django.core.exceptions.SuspiciousOperation`.

When :setting:`DEBUG` is ``True`` and ``ALLOWED_HOSTS`` is empty, the host
is validated against ``['localhost', '127.0.0.1', '[::1]']``.



This validation only applies via :meth:`~django.http.HttpRequest.get_host()`;
if your code accesses the ``Host`` header directly from ``request.META`` you
are bypassing this security protection.

.. setting:: APPEND_SLASH

``APPEND_SLASH``
----------------

Default: ``True``

When set to ``True``, if the request URL does not match any of the patterns
in the URLconf and it doesn't end in a slash, an HTTP redirect is issued to the
same URL with a slash appended. Note that the redirect may cause any data
submitted in a POST request to be lost.

The :setting:`APPEND_SLASH` setting is only used if
:class:`~django.middleware.common.CommonMiddleware` is installed
. See also :setting:`PREPEND_WWW`.

.. setting:: CACHES

``CACHES``
----------

Default::

    {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
