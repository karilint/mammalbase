import pytest
from django.contrib.auth import get_user_model
from imports.validation import ImportValidator
from mb.models import Collection, CollectionAttribute, ChoiceValue

User = get_user_model()


@pytest.mark.django_db
class TestImportValidator:
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.collection = Collection.objects.create(
            name='Test Collection',
            description='Test Description',
            created_by=self.user,
            updated_by=self.user
        )
        
        self.attribute = CollectionAttribute.objects.create(
            collection=self.collection,
            name='test_attribute',
            label='Test Attribute',
            attribute_type='choice',
            created_by=self.user,
            updated_by=self.user
        )
        
        # Create choice values with created_by and updated_by
        self.choice1 = ChoiceValue.objects.create(
            attribute=self.attribute,
            value='choice1',
            label='Choice 1',
            created_by=self.user,
            updated_by=self.user
        )
        self.choice2 = ChoiceValue.objects.create(
            attribute=self.attribute,
            value='choice2',
            label='Choice 2',
            created_by=self.user,
            updated_by=self.user
        )
        
        self.validator = ImportValidator(self.collection)

    def test_validate_choice_value_valid(self):
        """Test validation of valid choice value"""
        self.setUp()
        result = self.validator.validate_choice_value(
            'test_attribute',
            'choice1'
        )
        assert result is True

    def test_validate_choice_value_invalid(self):
        """Test validation of invalid choice value"""
        self.setUp()
        result = self.validator.validate_choice_value(
            'test_attribute',
            'invalid_choice'
        )
        assert result is False

    def test_validate_choice_value_nonexistent_attribute(self):
        """Test validation with non-existent attribute"""
        self.setUp()
        result = self.validator.validate_choice_value(
            'nonexistent_attribute',
            'choice1'
        )
        assert result is False

    def test_validate_row_valid_data(self):
        """Test validation of row with valid data"""
        self.setUp()
        row_data = {
            'test_attribute': 'choice1'
        }
        errors = self.validator.validate_row(row_data, row_num=1)
        assert len(errors) == 0

    def test_validate_row_invalid_choice(self):
        """Test validation of row with invalid choice"""
        self.setUp()
        row_data = {
            'test_attribute': 'invalid_choice'
        }
        errors = self.validator.validate_row(row_data, row_num=1)
        assert len(errors) > 0
        assert any('invalid_choice' in error.lower() for error in errors)

    def test_validate_row_empty_value(self):
        """Test validation of row with empty value"""
        self.setUp()
        row_data = {
            'test_attribute': ''
        }
        errors = self.validator.validate_row(row_data, row_num=1)
        # Empty values should be allowed
        assert len(errors) == 0
