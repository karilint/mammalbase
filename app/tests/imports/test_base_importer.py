from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from imports.base_importer import BaseImporter
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
