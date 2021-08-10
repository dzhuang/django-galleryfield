from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    path('upload/',
         login_required(views.BuiltInImageCreateView.as_view()),
         name="builtingalleryimage_upload"),
    path('crop/<int:pk>',
         login_required(views.BuiltInImageCropView.as_view()),
         name="builtingalleryimage_crop"),
    path('fetch/',
         login_required((views.BuiltInImageListView.as_view())),
         name="builtingalleryimage_fetch"),
]
