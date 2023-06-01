from django import forms

from django.core import validators

class MeasurementsForm(forms.Form):
    user_email = forms.EmailField(validators=[validators.EmailValidator(message="Invalid email address")],
        #widget=forms.widgets.TextInput(
        #attrs={
        #    "placeholder": "Enter your email address"
        #}
    )
