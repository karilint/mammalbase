from unittest import mock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from imports.importers.base_importer import BaseImporter
from middleware.current_user import _user

User = get_user_model()


class TestBaseImporter(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_author = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.importer = BaseImporter()
        
        client = Client()
        client.force_login(self.test_author)
        _user.value = self.test_author


    def test_get_or_create_source_location_returns_none_for_none(self):
        result = self.importer.get_or_create_source_location(None, source_reference=None, author=self.test_author)
        self.assertIsNone(result)


    @mock.patch("imports.importers.base_importer.SourceLocation.save")
    def test_get_or_create_source_location_handles_coord_text_schema_drift(self, save_mock):
        save_mock.side_effect = Exception("(1364, \"Field 'coord_text' doesn't have a default value\")")
        result = self.importer.get_or_create_source_location('Somewhere', source_reference=None, author=self.test_author)
        self.assertIsNone(result)


    @mock.patch("imports.importers.base_importer.SourceLocation.save")
    def test_get_or_create_source_location_handles_coord_text_cannot_be_null(self, save_mock):
        save_mock.side_effect = Exception("(1048, \"Column 'coord_text' cannot be null\")")
        result = self.importer.get_or_create_source_location('Somewhere', source_reference=None, author=self.test_author)
        self.assertIsNone(result)
