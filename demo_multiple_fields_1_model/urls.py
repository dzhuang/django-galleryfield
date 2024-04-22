from demo_multiple_fields_1_model import image_views
from django.urls import path

urlpatterns = [
    path(
        "upload1/",
        image_views.MyImage1CreateView.as_view(),
        name="demo_multiple_fields_1_model-myimage1-upload",
    ),
    path(
        "fetch1/",
        (image_views.MyImage1ListView.as_view()),
        name="demo_multiple_fields_1_model-myimage1-fetch",
    ),
    path(
        "crop1/<int:pk>",
        image_views.MyImage1CropView.as_view(),
        name="demo_multiple_fields_1_model-myimage1-crop",
    ),
    path(
        "upload2/",
        image_views.MyImage2CreateView.as_view(),
        name="demo_multiple_fields_1_model-myimage2-upload",
    ),
    path(
        "fetch2/",
        (image_views.MyImage2ListView.as_view()),
        name="demo_multiple_fields_1_model-myimage2-fetch",
    ),
    path(
        "crop2/<int:pk>",
        image_views.MyImage2CropView.as_view(),
        name="demo_multiple_fields_1_model-myimage2-crop",
    ),
]
