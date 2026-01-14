import pytest
from django.contrib.auth import get_user_model

from imports.validation_lib.base_validation import Validation
from mb.models import ChoiceValue
from middleware.current_user import _user

User = get_user_model()


@pytest.mark.django_db
class TestValidationChoiceValue:
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        _user.value = self.user
        ChoiceValue.objects.create(
            choice_set='Gender',
            caption='Male'
        )
        self.validator = Validation()

    def test_validate_choice_value_valid(self):
        self.setUp()
        data = {'sex': 'Male'}
        rules = {'sex': 'choiceValue:Gender'}
        errors = self.validator.validate(data, rules)
        assert errors == []

    def test_validate_choice_value_invalid(self):
        self.setUp()
        data = {'sex': 'Invalid'}
        rules = {'sex': 'choiceValue:Gender'}
        errors = self.validator.validate(data, rules)
        assert len(errors) == 1
