GALLERY_WIDGET_UI_DEFAULT_OPTIONS = {
    "autoUpload": "false",
    "imageMaxWidth": 1024,
    "imageMaxHeight": 1024,
    "loadImageFileTypes": r"/^image\/(gif|jpeg|png|svg\+xml)$/",
    "sequentialUploads": "true",
    "acceptFileTypes": r"/(\.|\/)(png|gif|jpe?g)$/i",
    "imageOrientation": "true",
    "maxNumberOfFiles": 10,
    "previewMaxWidth": 80,
    "previewMaxHeight": 80,
    "maxFileSize": 1.5 * 1024 ** 2,  # 1.5Mb
    "minFileSize": 0.0001 * 1024 ** 2,  # 0.0001Mb
    "disableImageResize": "/Android(?!.*Chrome)|Opera/.test(window.navigator && navigator.userAgent)",
}
