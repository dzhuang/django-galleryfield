v2.0.1 (2022-07-14)
------------------------------------

- Breaking changes (`#25 <https://github.com/dzhuang/django-galleryfield/pull/25>`__ , `#28 <https://github.com/dzhuang/django-galleryfield/pull/28>`__):

  - Added required method :meth:`create_instance_from_form` in ``ImageCreateView`` when customizing ``target_model`` .
  - Added required method :meth:`create_cropped_instance_from_form` in ``ImageCropView`` when customizing ``target_model`` .
  - Allowed customize image URL via :meth:`get_image_url` in ``target_model``.
  - Allowed customize image Crop URL via :meth:`get_crop_url` in ``target_model``.
  - Allowed customize image object serialization by :meth:`serialize_extra` in ``target_model``.
  - Bundled most static assets (except ``Bootstrap`` and ``jQuery``) into ``galleryfield-ui.js``, thus we no longer need to
    do extra configurations serving those static files locally.

      - Added option ``bootstrap_version`` in ``DJANGO_GALLERY_FIELD_CONFIG``, defaults to ``3``.
      - Removed all items in ``DJANGO_GALLERY_FIELD_CONFIG["assets"]`` except ``extra_js`` and ``extra_css``.
      - Added new options ``jquery``, ``bootstrap_css`` and ``bootstrap_js`` to ``DJANGO_GALLERY_FIELD_CONFIG["assets"]``, with
        CDN URL of those assets as default values.

  - Dropped ``jQuery-UI`` in favor of ``SortableJS`` for sorting uploaded images. Added ``jquery_file_upload_ui_sortable_options`` in ``DJANGO_GALLERY_FIELD_CONFIG`` .
  - Allowed use ``Bootstrap`` 4 and 5 via settings configurations.


v1.5.1 (2022-05-17)
------------------------------------

- Fixes: updated rollup scripts. (`f1e2207 <https://github.com/dzhuang/django-galleryfield/commit/f1e2207fccd16d15c0d2405b575341f32d777bcd>`__)
- Fixes: added back lost indicator in upload UI. (`6177b34 <https://github.com/dzhuang/django-galleryfield/commit/6177b34cb239e96982976efd770940c715cd4c6e>`__)


v1.5.0 (2022-05-16)
------------------------------------

- Refactor: used rollup.js to manage static assets. (`#24 <https://github.com/dzhuang/django-galleryfield/pull/24>`__)


v1.4.5 (2022-05-12)
------------------------------------

- Fixes: fixed ``get_image_url`` in ``BaseImageModelMixin``. (`#21 <https://github.com/dzhuang/django-galleryfield/pull/21>`__)


v1.4.4 (2022-05-12)
------------------------------------

- Fixes: fixed ``upload_template`` and ``download_template`` override after widget initialization. (`#20 <https://github.com/dzhuang/django-galleryfield/pull/20>`__)


v1.4.3 (2022-05-12)
------------------------------------

- Features: added ``JS_DOWNLOAD_TEMPLATE_NAME`` block. (`#19 <https://github.com/dzhuang/django-galleryfield/pull/19>`__)


v1.4.2 (2022-05-12)
------------------------------------

- Features: allowed override ``image_url`` and ``crop_url`` when serializing image objects. Allow override ``upload_template`` and ``download_template``. (`#16 <https://github.com/dzhuang/django-galleryfield/pull/16>`__)

- Fixes: fixed upload UI checkbox of items. (`#18 <https://github.com/dzhuang/django-galleryfield/pull/18>`__)


v1.4.1 (2022-05-06)
------------------------------------

- Features: changed image handling view URL naming rule to include ``app_label`` prefix. (`#11 <https://github.com/dzhuang/django-galleryfield/pull/11>`__)
- Features: changed getting cookie name via Django settings ``CSRF_COOKIE_NAME``. (`#14 <https://github.com/dzhuang/django-galleryfield/pull/14>`__)


v1.2.7-beta (2021-08-22)
------------------------------------

- Breaking changes: renamed project from ``django-gallery-widget`` to ``django-galleryfield``.


v1.2.6-beta (2021-08-18)
------------------------------------

- Fixes: removed default ``target_model`` in ``ListView`` (``BaseListViewMixin``).

v1.2.5-beta (2021-08-12)
------------------------------------

Initial release.
