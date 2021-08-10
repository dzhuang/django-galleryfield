from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

# The default view names also follow the form of "model_name-upload".

urlpatterns = [
    path('upload/',
         login_required(views.BuiltInImageCreateView.as_view()),
         name="gallery_image_upload"),
    path('crop/<int:pk>',
         login_required(views.BuiltInImageCropView.as_view()),
         name="gallery_image_crop"),
    path('fetch/',
         login_required((views.BuiltInImageListView.as_view())),
         name="gallery_images_fetch"),
]
