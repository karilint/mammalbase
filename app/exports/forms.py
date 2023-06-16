from django import forms
from django.core import validators


BROADERTERMS_CHOICES = [
    ("Standard measurements", "Standard measurements"),
    ("Cranial measurements", "Cranial measurements"),
]


class MeasurementsForm(forms.Form):
    user_email = forms.EmailField(validators=[validators.EmailValidator(message="Invalid email address")],
        #widget=forms.widgets.TextInput(
        #attrs={
        #    "placeholder": "Enter your email address"
        #}
    )

    export_choices = forms.MultipleChoiceField(
            required=True,
            widget=forms.CheckboxSelectMultiple(attrs={'class': 'export_checkboxes'}),
            choices=BROADERTERMS_CHOICES,
            label="Select type of data to be exported"
    )
