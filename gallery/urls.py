from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views
from . import mixins

urlpatterns = [
    # path('upload/', views.upload, name="gallery_image_upload"),
    path('upload/', login_required(views.ImageCreateView.as_view()), name="gallery_image_upload"),
    path('crop/', views.crop, name="gallery_image_crop"),
    path('fetch/', views.fetch, name="gallery_images_fetch"),
]
