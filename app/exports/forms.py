from django import forms
from django.core import validators


BROADERTERMS_CHOICES = [
    ('Standard measurements', 'Standard measurements'),
    ('Cranial measurements', 'Cranial measurements'),
]


class MeasurementsForm(forms.Form):
    user_email = forms.EmailField(validators=[validators.EmailValidator(message='Invalid email address')],
    )

    export_choices = forms.MultipleChoiceField(
            required=True,
            widget=forms.CheckboxSelectMultiple(attrs={'class': 'export_checkboxes'}),
            choices=BROADERTERMS_CHOICES,
            label='Select the type of data to be exported',
            error_messages={'required': 'Please select at least one type of data to be exported.'}
    )
