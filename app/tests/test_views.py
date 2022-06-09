from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import tempfile, csv, os
import imports.views as views


class ImportViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='Testi')
        self.client.force_login(self.user)
        self.res = {'status': 'ok', 
                'message-type': 'work-list', 
                'message-version': '1.0.0', 
                'message': {'items': [{
                                        'publisher': 'Wildlife ent Society', 
                                        'issue': '20', 
                                        'DOI': '12.12345/jott.1234.12.1.12345-12345', 
                                        'type': 'journal-article', 
                                        'created': {'date-parts': [[2022, 2, 26]], 'date-time': '2022-02-26T13:24:30Z', 'timestamp': 1645881870000}, 
                                        'page': '20539-20549', 
                                        'source': 'Crossref', 
                                        'is-referenced-by-count': 0, 
                                        'title': ['Testing, testing'],
                                        'volume': '20', 
                                        'author': [{'given': 'Teresa', 'family': 'Tester', 'sequence': 'first', 'affiliation': []},
                                                    {'given': 'Timothy', 'family': 'TesterToo', 'sequence': 'additional', 'affiliation': []}], 
                                        'member': '4876', 
                                        'published-online': {'date-parts': [[2022, 2, 26]]}, 
                                        'deposited': {'date-parts': [[2022, 2, 26]], 'date-time': '2022-02-26T13:25:01Z', 'timestamp': 1645881901000}, 
                                        'issued': {'date-parts': [[2022, 2, 26]]}, 
                                        'references-count': 54,
                                        'container-title': ['Testing container-title'], 
                                        'journal-issue': {'issue': '2', 'published-online': {'date-parts': [[2022, 2, 26]]}}, 
                                        'URL': 'http://dx.doi.org/10.11609/jott.6786.14.2.20539-20549', 
                                        'ISSN': ['0974-7907', '0974-7893'], 
                                        'issn-type': [{'value': '0974-7907', 'type': 'electronic'}, {'value': '0974-7893', 'type': 'print'}], 
                                        'published': {'date-parts': [[2022, 2, 26]]}}], 
                                        'items-per-page': 1, 'query': {'start-index': 0, 'search-terms': None}}}
        #self.user = User.objects.create_user('testi', 'testi@jotain.com', '1234')
        #self.client.login(username='testi', password='1234')
    
    def test_import_test_view(self):
        response = self.client.get('/import/test')
        self.assertEqual(response.status_code, 200)
    
    def test_import_test_reverse(self):
        response = self.client.get(reverse('import_test'))
        self.assertEqual(response.status_code, 200)

    def test_create_masterreference(self):
        answer = views.create_masterreference('Tester, T., TesterToo, T., Testing, testing', self.res)
        self.assertEquals(answer, True)

    def test_create_masterreference_with_wrong_title(self):
        answer = views.create_masterreference('Tester, T., TesterToo, T., Testing, not testing at all', self.res)
        self.assertEquals(answer, False)

    
