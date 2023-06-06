from django import forms

from django.core import validators

DUMMY_CHOICES = [
    ("cranial measurements", "Cranial measurements"),
    ("postcranial measurements", "Postcranial measurements"),
    ("external measurements", "External measurements"),
]


class MeasurementsForm(forms.Form):
    user_email = forms.EmailField(validators=[validators.EmailValidator(message="Invalid email address")],
        #widget=forms.widgets.TextInput(
        #attrs={
        #    "placeholder": "Enter your email address"
        #}
    )
    select_fields_to_be_exported = forms.MultipleChoiceField(required=True,
                                          widget=forms.CheckboxSelectMultiple,
                                          choices= DUMMY_CHOICES
                                          )