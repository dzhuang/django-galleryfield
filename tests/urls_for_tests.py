from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from tests import views_for_tests as fake_views

urlpatterns = [
    path('demo/', include("demo.urls")),
    path(r"image-handler/", include("galleryfield.urls")),
    path('test-upload/', fake_views.fake_upload, name="test_image_upload"),
    path('test-crop/', fake_views.fake_crop, name="test_image_crop"),
    path('test-fetch/', fake_views.fake_fetch, name="test_images_fetch"),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
