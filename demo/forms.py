from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from gallery.widgets import GalleryWidget

from demo.models import DemoGallery


class GalleryForm(forms.ModelForm):
    class Meta:
        model = DemoGallery
        fields = ["images"]
        labels = {'images': ""}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["images"].widget = GalleryWidget()
        self.fields["images"].required = False

        self.helper = FormHelper(self)
        self.helper.layout.append(Submit("Submit", "submit"))
