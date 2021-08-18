from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from demo.models import DemoGallery


class GalleryForm(forms.ModelForm):
    class Meta:
        model = DemoGallery
        fields = ["images"]

        # Remove label
        labels = {'images': ""}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields["images"].required = False

        # self.fields["images"].max_number_of_images = 2

        from django.forms.widgets import Textarea  # noqa

        # self.fields["images"].widget = Textarea()
        # self.fields["images"].widget.attrs["readonly"] = True

        self.helper = FormHelper(self)
        self.helper.layout.append(
            Submit("Submit", "submit",
                   css_class="gallery-widget-submit-button"))
