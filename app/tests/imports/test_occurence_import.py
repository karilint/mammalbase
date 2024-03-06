from django.test import TestCase
import requests_mock
from django.contrib.auth.models import User
from .utils.mock_api import generate_mock_api
from allauth.socialaccount.models import SocialAccount
from django.test import Client
from django.contrib.messages import get_messages

class OccurenceImporterTest(TestCase):
    @requests_mock.Mocker()
    def setUp(self, mock_api):
        generate_mock_api(mock_api)
        self.test_author = User.objects.create_superuser(username='Testi')
        self.social_account = SocialAccount.objects.create(uid='1111-1111-2222-222X', user_id=self.test_author.pk)
        self.client.force_login(self.test_author)
        
    def test_import_valid_occurences(self):
        with open('tests/imports/assets/occurence/valid_occurences_file.csv', 'r') as fp:
            response = self.client.post('/import/occurrences', {'csv_file': fp})
            print(get_messages(response.wsgi_request))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        print(messages[0])
        self.assertEqual(str(messages[0]), 'The author 0000-0000-0000-000X is not a valid ORCID ID at row 2.')
        self.assertEqual(response.status_code, 302)
        
    def test_import_invalid_occurences(self):
        with open('tests/imports/assets/occurence/invalid_occurences_file.csv', 'r') as fp:
            response = self.client.post('/import/occurrences', {'csv_file': fp})
            print(get_messages(response.wsgi_request))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        print(messages[0])
        self.assertEqual(str(messages[0]), 'The author 0000-0000-0000-000X is not a valid ORCID ID at row 2.')
        self.assertEqual(response.status_code, 302)