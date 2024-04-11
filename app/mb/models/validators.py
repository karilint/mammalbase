""" mb.models.validators - Validators used in mb.models """

# What the hell is this? Should name "_" be reserved for something???
# First appeared in this commit:
# https://github.com/karilint/mammalbase/commit/90d7df61c8b5297b59817393604137bf4c46a973

# For doi validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_doi(value):
    if not value.startswith( '10.' ):
        raise ValidationError(
            _('Value "%(value)s" does not begin with 10 followed by a period'),
            params={'value': value},
        )

