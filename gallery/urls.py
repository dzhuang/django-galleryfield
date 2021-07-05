from django.urls import path

from .configs import GALLERY_DELETE_URL_NAME, GALLERY_UPLOAD_HANDLER_URL_NAME

from . import views

urlpatterns = [
    path('upload/', views.upload, name=GALLERY_UPLOAD_HANDLER_URL_NAME),
    path(r'delete/<int:pk>/', views.upload_delete, name=GALLERY_DELETE_URL_NAME),
]
