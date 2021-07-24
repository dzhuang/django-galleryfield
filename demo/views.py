from django.urls import reverse
from django.views.generic.edit import UpdateView, CreateView

from demo.models import DemoGallery
from demo.forms import GalleryForm


class GalleryFormView(CreateView):
    form_class = GalleryForm
    template_name = "form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_description"] = "Create new gallery"
        return context

    def get_success_url(self):
        return reverse("gallery-update", kwargs={"pk": self.object.pk})


class GalleryUpdateView(UpdateView):
    model = DemoGallery
    form_class = GalleryForm
    template_name = "form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_description"] = "Update gallery"
        return context
