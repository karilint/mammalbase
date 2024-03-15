from django import forms
from mb.models import AttributeRelation

class AttributeRelationForm(forms.ModelForm):
    class Meta:
        model = AttributeRelation
        fields = ['source_attribute', 'master_attribute']
        
        widgets = {
            'source_attribute': forms.HiddenInput(),
        }