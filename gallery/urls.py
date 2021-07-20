from django.urls import path

from . import views

urlpatterns = [
    path('upload/', views.upload, name="gallery_image_upload"),
    path('crop/', views.crop, name="gallery_image_crop"),
]
