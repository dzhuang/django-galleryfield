from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from demo_custom.models import CustomDemoGallery


class CustomGalleryForm(forms.ModelForm):
    class Meta:
        model = CustomDemoGallery
        fields = ["images"]

        # Remove label
        labels = {'images': ""}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["images"].widget.download_template = (
            "demo_custom/custom_download_template.html")

        self.helper = FormHelper(self)
        self.helper.layout.append(
            Submit("Submit", "submit",
                   css_class="gallery-widget-submit-button"))
