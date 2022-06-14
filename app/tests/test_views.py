from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
import tempfile, csv, os
import imports.views as views
import pandas as pd


class ImportViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='Testi')
        self.client.force_login(self.user)
        self.res = {'status': 'ok', 
                'message-type': 'work-list', 
                'message-version': '1.0.0', 
                'message': {'items': [
                                        {'publisher': 'Wildlife ent Society', 
                                        'issue': '2', 
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
                                        'published': {'date-parts': [[2022, 2, 26]]}},
                                        {'publisher': 'Wildlife ent Society', 
                                        'issue': '20', 
                                        'DOI': '12.12345/jott.1234.12.1.12345-12345', 
                                        'type': 'journal-article', 
                                        'created': {'date-parts': [[2022, 2, 26]], 'date-time': '2022-02-26T13:24:30Z', 'timestamp': 1645881870000}, 
                                        'page': '20539-20549', 
                                        'title': ['Testing, not testing'],
                                        'volume': '20', 
                                        'author': [{'given': 'Teresa', 'family': 'Tester', 'sequence': 'first', 'affiliation': []},
                                                    {'given': 'Timothy', 'family': 'TesterToo', 'sequence': 'additional', 'affiliation': []}], 
                                        'container-title': ['Testing container-title'], 
                                        'journal-issue': {'issue': '2', 'published-online': {'date-parts': [[2022, 2, 26]]}}, 
                                        'URL': 'http://dx.doi.org/10.11609/jott.6786.14.2.20539-20549', 
                                        'ISSN': ['0974-7907', '0974-7893'], 
                                        'issn-type': [{'value': '0974-7907', 'type': 'electronic'}, {'value': '0974-7893', 'type': 'print'}], 
                                        'published': {'date-parts': [[2022, 2, 26]]}}
                                        ]}, 
                                        'items-per-page': 2, 'query': {'start-index': 0, 'search-terms': None}}
        #self.user = User.objects.create_user('testi', 'testi@jotain.com', '1234')
        #self.client.login(username='testi', password='1234')
    
    def test_import_test_view(self):
        response = self.client.get('/import/test')
        #print('helo', response.content, 'helo', response.client, response.context)
        self.assertEqual(response.status_code, 200)
    
    def test_import_test_reverse(self):
        response = self.client.get(reverse('import_test'))
        self.assertEqual(response.status_code, 200)

    def test_import_post(self):
        with open('test_post.csv', 'w') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(['author', 'verbatimScientificName', 'taxonRank', 'verbatimLocality', 'habitat', 'samplingEffort', 'sex', 'individualCount', 'verbatimEventDate', 'measurementMethod', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue', 'associatedReferences',  'references'])
            #rivi 10 mallissa
            writer.writerow(['0000-0001-9627-8821', 'Lagothrix flavicauda', 'Species', '', '', '', '', '', '', '',  'primarily frugivorous', '1','', 'Leo Luna 1980 | deLuycker 2007 | S. Shanee and N. Shanee 2011b | Shanee 2014a | Fack et al. 2018a','Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 11 mallissa
            writer.writerow(['0000-0001-9627-8821', 'Lagothrix flavicauda',	'Species', '', '', '', '', '', '', '',  'leaves', '2', '', 'Leo Luna 1980 | deLuycker 2007 | S. Shanee and N. Shanee 2011b | Shanee 2014a | Fack et al. 2018a', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 17 mallissa
            writer.writerow(['0000-0001-9627-8821',	'Lagothrix flavicauda',	'Species', '', '', '15-month-study', '', '', 'October 2009-June 2010 and August 2010-February 2011', '', 'fruit', '1', '46.3', 'S. Shanee (2014)', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 23 mallissa
            writer.writerow(['0000-0001-9627-8821',	'Lagothrix flavicauda',	'Species',	'', '', '', '', '', '', 'observations of fruit consumption', 'fruits of Ficus',	'1', '43', 'S. Shanee and N. Shanee 2011b',	'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 38 mallissa
            writer.writerow(['0000-0001-9627-8821',	'Capra hircus',	'Species', 'Mandu Mandu Gorge, Cape Range National Park, Western Australia', 'Summer (February, March, April and October)', '', '', '108', 'between February and October 2006', 'The percentage of plant species found in scats.', 'Unidentiﬁed monocots', '1','36.8', 'Original study', 'Creese, S., Davies, S.J. and Bowen, B.J., 2019. Comparative dietary analysis of the black-flanked rock-wallaby (Petrogale lateralis lateralis), the euro (Macropus robustus erubescens) and the feral goat (Capra hircus) from Cape Range National Park, Western Australia. Australian Mammalogy, 41(2), pp.220-230.'])
        with open('test_post.csv', 'r') as fp:
            response = self.client.post('/import/test', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual('File imported successfully.' in str(messages[0]), True)
        self.assertEqual(response.status_code, 302)

    def test_import_post_failing_file(self):
        with open('test_bad.csv', 'w') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(['writer', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue',  'references'])
            writer.writerow(['0000-0001-9627-8821', 'Lagothrix flavicauda Lagothrix flavicauda', 'Species', 'primarily frugivorous', '1', '', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            writer.writerow(['0000-0001-9627-8821',	'Lagothrix flavicauda',	'animal',	'leaves', '2', '', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            writer.writerow(['0000-0001-9627-8821',	'Lagothrix flavicauda',	'Species',	'fruit', '1', '46.3a','Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
        with open('test_bad.csv', 'r') as fp:
            response = self.client.post('/import/test', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'The import file does not contain the required headers. The missing header is: author.')
        self.assertEqual(response.status_code, 302)
            
    def test_import_post_wrong_file(self):
        with open('tests/test_tools.py', 'r') as fp:
            response = self.client.post('/import/test', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1) 
        self.assertEqual('Unable to upload file.' in str(messages[0]), True)
        self.assertEqual(response.status_code, 302)

    def test_create_masterreference(self):
        answer = views.create_masterreference('Tester, T., TesterToo, T., Testing, testing', self.res)
        self.assertEquals(answer, True)

    def test_create_masterreference_with_wrong_title(self):
        answer = views.create_masterreference('Tester, T., TesterToo, T., Testing, not testing at all', self.res)
        self.assertEquals(answer, False)

    def test_title_matches_citation_correct(self):
        answer = views.title_matches_citation('<i>This is a correct title</i>', 'This is a correct title')
        self.assertEquals(answer, True)
    
    def test_title_matches_citation_false(self):
        answer = views.title_matches_citation('This is not a correct title', 'This is a correct title')
        self.assertEquals(answer, False)

    def test_make_harvard_citation_journalarticle(self):
        test_citation = views.make_harvard_citation_journalarticle('Testing, testing', 'doi123', ['Tester, T.', 'TesterToo, T.', 'TesterThree, T.'],
                                                                        '2022', 'Testing container-title', '20', '2', '123-321')
        self.assertEquals('Tester, T., TesterToo, T., TesterThree, T. 2022. Testing, testing. Testing container-title. 20(2), pp.123-321. Available at: doi123.', test_citation)

    
