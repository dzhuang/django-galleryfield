from django.contrib.auth.decorators import login_required
from django.urls import path

from galleryfield import image_views

# The default view names also follow the form of "app_label-model_name-upload".

urlpatterns = [
    path('upload/',
         login_required(image_views.BuiltInImageCreateView.as_view()),
         name="galleryfield-builtingalleryimage-upload"),
    path('fetch/',
         login_required((image_views.BuiltInImageListView.as_view())),
         name="galleryfield-builtingalleryimage-fetch"),
    path('crop/<int:pk>',
         login_required(image_views.BuiltInImageCropView.as_view()),
         name="galleryfield-builtingalleryimage-crop"),
]
