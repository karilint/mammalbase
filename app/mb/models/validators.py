""" mb.models.validators - Validators used in mb.models """

# For doi validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy

def validate_doi(value):
    if not value.startswith( '10.' ):
        raise ValidationError(
            gettext_lazy(
                    'Value "%(value)s" does not begin '
                    'with 10 followed by a period'),
            params={'value': value},
        )

