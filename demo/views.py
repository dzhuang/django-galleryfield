from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from demo.forms import GalleryForm
from demo.models import DemoGallery


class GalleryFormView(LoginRequiredMixin, CreateView):
    form_class = GalleryForm
    template_name = "form.html"
    extra_context = {
        "form_description": "Create new gallery_widget"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_description"] = "Create new gallery_widget"
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("gallery-update", kwargs={"pk": self.object.pk})


class GalleryUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = DemoGallery
    form_class = GalleryForm
    template_name = "form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_description"] = "Update gallery_widget"
        context["detail_view_url"] = reverse(
            "gallery-detail", kwargs={"pk": self.object.pk})
        return context

    def test_func(self):
        return (self.request.user == self.get_object().owner
                or self.request.user.is_superuser)


class GalleryDetailView(DetailView):
    # Anonymous user can visit this.

    model = DemoGallery

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_description"] = "Gallery Detail"
        context["update_view_url"] = reverse(
            "gallery-update", kwargs={"pk": self.object.pk})
        return context
