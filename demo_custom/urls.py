from django.contrib.auth.decorators import login_required
from django.urls import path, re_path

from demo_custom import image_views, views

urlpatterns = [
    # image handle views

    path(r'upload/',
         login_required(image_views.CustomImageCreateView.as_view()),
         name="demo_custom-customimage-upload"),
    path(r'fetch/',
         login_required((image_views.CustomImageListView.as_view())),
         name="demo_custom-customimage-fetch"),
    path(r'crop/<int:pk>',
         login_required(image_views.CustomImageCropView.as_view()),
         name="customimage-crop"),

    # gallery views
    path(r'', views.CustomGalleryCreateView.as_view(), name='custom-gallery'),
    path('update/<int:pk>',
         views.CustomGalleryUpdateView.as_view(), name='custom-gallery-update'),
    path('detail/<int:pk>',
         views.CustomGalleryDetailView.as_view(), name='custom-gallery-detail'),

    re_path(r"^user_images"
            + r"/(?P<user_id>\d+)"
            r"/(?P<image_id>\d+)"
            r"/(?P<file_name>[^/]+)$",
            image_views.image_download,
            name="image_download"),
]
