from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import tempfile, csv, os

class ImportViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='Testi')
        self.client.force_login(self.user)
        #self.user = User.objects.create_user('testi', 'testi@jotain.com', '1234')
        #self.client.login(username='testi', password='1234')
    
    def test_import_test_view(self):
        response = self.client.get('/import/test')
        self.assertEqual(response.status_code, 200)
    
    def test_import_test_reverse(self):
        response = self.client.get(reverse('import_test'))
        self.assertEqual(response.status_code, 200)