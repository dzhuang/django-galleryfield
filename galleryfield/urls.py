from django.contrib.auth.decorators import login_required
from django.urls import path

from galleryfield import views

# The default view names also follow the form of "model_name-upload".

urlpatterns = [
    path('upload/',
         login_required(views.BuiltInImageCreateView.as_view()),
         name="builtingalleryimage-upload"),
    path('fetch/',
         login_required((views.BuiltInImageListView.as_view())),
         name="builtingalleryimage-fetch"),
    path('crop/<int:pk>',
         login_required(views.BuiltInImageCropView.as_view()),
         name="builtingalleryimage-crop"),
]
