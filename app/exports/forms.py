from django import forms
from django.core import validators


BROADERTERMS_CHOICES = [
    ("standard measurements", "Standard measurements"),
    ("cranial measurements", "Cranial measurements"),
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
            widget=forms.CheckboxSelectMultiple,
            choices=BROADERTERMS_CHOICES,
            label="Select type of data to be exported"
    )
