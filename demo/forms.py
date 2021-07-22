from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from demo.models import DemoGallery
from django.forms.widgets import Textarea


class GalleryForm(forms.ModelForm):
    class Meta:
        model = DemoGallery
        fields = ["images"]

        # Uncomment to remove label
        # labels = {'images': ""}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["images"].required = False

        # self.fields["images"].widget = Textarea()
        self.helper = FormHelper(self)
        self.helper.layout.append(
            Submit("Submit", "submit",
                   css_class="gallery-widget-submit-button"))
