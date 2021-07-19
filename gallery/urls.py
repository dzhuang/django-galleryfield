from django.urls import path


from .conf import (
    DEFAULT_UPLOAD_HANDLER_URL_NAME, DEFAULT_CROP_URL_NAME)

from . import views

urlpatterns = [
    path('upload/', views.upload, name=DEFAULT_UPLOAD_HANDLER_URL_NAME),
    path('crop/', views.crop, name=DEFAULT_CROP_URL_NAME),
]
