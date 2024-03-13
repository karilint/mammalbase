from django import forms
from mb.models import SourceAttribute

class SourceAttributeForm(forms.ModelForm):
    class Meta:
        model = SourceAttribute
        fields = ['name']