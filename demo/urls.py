"""gallery_widget URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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

    path(r"images-handler/", include("gallery_widget.urls")),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
