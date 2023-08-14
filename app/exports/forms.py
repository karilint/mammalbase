from django import forms

# BROADERTERMS: ('value will be same as the name of master attribute group', 'display value on screen')
BROADERTERMS = [
    ('External measurements', 'External measurements'),
    ('Cranial measurements', 'Cranial measurements'),
]


class ETSForm(forms.Form):
    user_email = forms.EmailField(
    )

    export_choices = forms.MultipleChoiceField(
            required=True,
            widget=forms.CheckboxSelectMultiple(attrs={'class': 'export_checkboxes'}),
            choices=BROADERTERMS,
            label='Select the type of data to be exported',
            error_messages={'required': 'Please select at least one type of data to be exported.'}
    )
