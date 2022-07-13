from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from demo_custom.forms import CustomGalleryForm
from demo_custom.models import CustomDemoGallery

# class GalleryEditPermissionTestMixin(UserPassesTestMixin):
#     raise_exception = True
#
#     def test_func(self):
#         user_id = int(self.kwargs["user_id"])
#         try:
#             user = get_object_or_404(get_user_model(), id=user_id)
#         except Exception:
#             return False
#         else:
#             if self.request.user.is_superuser:
#                 return True
#             if self.request.user == user:
#                 return True
#             return False


class CustomGalleryCreateView(LoginRequiredMixin, CreateView):
    form_class = CustomGalleryForm
    template_name = "form.html"
    extra_context = {
        "form_description": "Create a new custom gallery"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("custom-gallery-update", kwargs={"pk": self.object.pk})


class CustomGalleryUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = CustomDemoGallery
    form_class = CustomGalleryForm
    template_name = "form.html"
    extra_context = {
        "form_description": "Update Custom Gallery"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["detail_view_url"] = reverse(
            "custom-gallery-detail", kwargs={"pk": self.object.pk})
        return context

    def test_func(self):
        return (self.request.user == self.get_object().creator
                or self.request.user.is_superuser)


class CustomGalleryDetailView(DetailView):
    # Anonymous user can visit this.

    model = CustomDemoGallery
    extra_context = {
        "form_description": "Custom Gallery Detail"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update_view_url"] = reverse(
            "custom-gallery-update", kwargs={"pk": self.object.pk})
        return context
