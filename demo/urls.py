from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from demo import views

urlpatterns = [
    path(r'', views.GalleryCreateView.as_view(), name='gallery'),
    path('gallery/<int:pk>',
         views.GalleryUpdateView.as_view(), name='gallery-update'),
    path('gallery-detail/<int:pk>',
         views.GalleryDetailView.as_view(), name='gallery-detail'),

    path(r"images-handler/", include("galleryfield.urls")),
    path('admin/', admin.site.urls),
]

urlpatterns += [path(r"custom/", include("demo_custom.urls"))]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
