import requests_mock
from allauth.socialaccount.models import SocialAccount
from django.test import Client, TestCase
from django.contrib.messages import get_messages
from django.contrib.auth.models import User
from mb.models import ChoiceValue
from .utils.mock_api import generate_mock_api

class OccurenceImporterTest(TestCase):
    @requests_mock.Mocker()
    def setUp(self, mock_api):
        generate_mock_api(mock_api)
        self.test_author = User.objects.create_superuser(username='Testi')
        self.social_account = SocialAccount.objects.create(uid='1111-1111-2222-2222', user_id=self.test_author.pk)
        self.client.force_login(self.test_author)
        ChoiceValue.objects.create(choice_set='Lifestage', caption='Adult')
        ChoiceValue.objects.create(choice_set='Lifestage', caption='Juvenile')
        ChoiceValue.objects.create(choice_set='Lifestage', caption='Subadult')
        ChoiceValue.objects.create(choice_set='Gender', caption='Male')
        ChoiceValue.objects.create(choice_set='Gender', caption='Female')
        
        
    def test_import_valid_occurences(self):
        with open('tests/imports/assets/occurence/valid_occurences_file.tsv', 'r') as fp:
            response = self.client.post('/import/occurrences', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), 'File imported successfully. 6 rows of data were imported.(0 rows were skipped.)')
        self.assertEqual(response.status_code, 302)

    def test_import_invalid_occurences(self):
        with open('tests/imports/assets/occurence/invalid_occurences_file.tsv', 'r') as fp:
            response = self.client.post('/import/occurrences', { 'name': 'fred', 'csv_file': fp})
            print(get_messages(response.wsgi_request))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 6)
        self.assertEqual(str(messages[0]), "Error on row: 1. Error: 'author' field must follow the following format: 0000-0000-0000-0000")
        self.assertEqual(response.status_code, 302)
        
    def test_author_consistency(self):
        with open('tests/imports/assets/occurence/author_consistency_file.tsv', 'r') as fp:
            response = self.client.post('/import/occurrences', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Authors need to be consisten. Please make sure each row has your own ORCID')
        self.assertEqual(response.status_code, 302)