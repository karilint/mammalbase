from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import User
from mb.models import EntityClass, SourceEntity, SourceLocation, SourceMethod, SourceReference
from imports.tools import Check
import imports.tools as tools
import tempfile, csv, os
import pandas as pd



class ToolsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('import/test')
        self.check = Check(self.request)
        self.user = User.objects.create_user(username='Testuser', password='12345')
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)

        setattr(self.request, '_messages', messages)
        with open('test.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['author', 'verbatimScientificName', 'taxonRank', 'verbatimLocality', 'habitat', 'samplingEffort', 'sex', 'individualCount', 'verbatimEventDate', 'measurementMethod', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue', 'associatedReferences',  'references'])
            #rivi 10 mallissa
            writer.writerow(['1111-1111-2222-222X', 'Lagothrix flavicauda', 'Species', '', '', '', '', '', '', '',  'primarily frugivorous', '1','', 'Leo Luna 1980 | deLuycker 2007 | S. Shanee and N. Shanee 2011b | Shanee 2014a | Fack et al. 2018a','Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 11 mallissa
            writer.writerow(['1111-1111-2222-222X', 'Lagothrix flavicauda',	'Species', '', '', '', '', '', '', '',  'leaves', '2', '', 'Leo Luna 1980 | deLuycker 2007 | S. Shanee and N. Shanee 2011b | Shanee 2014a | Fack et al. 2018a', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 17 mallissa
            writer.writerow(['1111-1111-2222-222X',	'Lagothrix flavicauda',	'Species', '', '', '15-month-study', '', '', 'October 2009-June 2010 and August 2010-February 2011', '', 'fruit', '1', '46.3', 'S. Shanee (2014)', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 23 mallissa
            writer.writerow(['1111-1111-2222-222X',	'Lagothrix flavicauda',	'Species',	'', '', '', '', '', '', 'observations of fruit consumption', 'fruits of Ficus',	'1', '43', 'S. Shanee and N. Shanee 2011b',	'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 38 mallissa
            writer.writerow(['1111-1111-2222-222X',	'Capra hircus',	'Species', 'Mandu Mandu Gorge, Cape Range National Park, Western Australia', 'Summer (February, March, April and October)', '', '', '108', 'between February and October 2006', 'The percentage of plant species found in scats.', 'Unidentiﬁed monocots', '1','36.8', 'Original study', 'Creese, S., Davies, S.J. and Bowen, B.J., 2019. Comparative dietary analysis of the black-flanked rock-wallaby (Petrogale lateralis lateralis), the euro (Macropus robustus erubescens) and the feral goat (Capra hircus) from Cape Range National Park, Western Australia. Australian Mammalogy, 41(2), pp.220-230.'])
        with open('false_test.csv', 'w') as file2:
            writer = csv.writer(file2)
            writer.writerow(['writer', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue',  'references'])
            writer.writerow(['1111-1111-2222-2222', 'Lagothrix flavicauda Lagothrix flavicauda', 'Species', 'primarily frugivorous', '1', '', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda',	'animal',	'leaves', '2', '', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda',	'Species',	'fruit', '1', '46.3a','Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
        with open('false_measurement_value.csv', 'w') as file3:
            writer = csv.writer(file3)
            writer.writerow(['writer', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue',  'references'])
            writer.writerow(['1111-1111-2222-2222', 'Lagothrix flavicauda Lagothrix flavicauda', 'Species', 'primarily frugivorous', '1', '5', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda',	'animal',	'leaves', '2', '10', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
        with open('false_file2.csv', 'w') as file4:
            writer = csv.writer(file4)
            writer.writerow(['writer', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue',  'references'])
            writer.writerow(['1111-1111-2222-2222', 'Lagothrix flavicauda flavicauda', 'Species', 'primarily frugivorous', '1', '', 'Book'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda flavicauda',	'Species',	'leaves', '2', '',  'Book'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda flavicauda',	'Species',	'fruit', '1', '',   'Book'])
        with open('false_vsn.csv', 'w') as file5:
            writer = csv.writer(file5)
            writer.writerow(['writer', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue',  'references'])
            writer.writerow(['1111-1111-2222-2222', 'Lagothrix flavicauda', 'Genus', 'primarily frugivorous', 'a', '5', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
        with open('false_sequence.csv', 'w') as file6:
            writer = csv.writer(file6)
            writer.writerow(['writer', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue',  'references'])
            writer.writerow(['1111-1111-2222-2222', 'Lagothrix flavicauda flavicauda', 'Species', 'primarily frugivorous', '1', '', 'Book'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda flavicauda',	'Species',	'leaves', '2', '',  'Book'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda flavicauda',	'Species',	'fruit', '4', '',   'Book'])


        self.file = pd.read_csv('test.csv')
        self.false_file = pd.read_csv('false_test.csv')
        self.false_measurement_value = pd.read_csv('false_measurement_value.csv')
        self.false_file2 = pd.read_csv('false_file2.csv')
        self.false_vsn = pd.read_csv('false_vsn.csv')
        self.false_sequence = pd.read_csv('false_sequence.csv')
        self.reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][1], self.user)
        self.dict = {'author': ['1111-1111-2222-2222', '1111-1111-2222-2233'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'hello'],
        'sequence':[1,1],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'] }
        self.entity = tools.get_entityclass(self.file.loc[:, 'taxonRank'][1], self.user)    
        #print(tools.get_entityclass(self.file.loc[:, 'taxonRank'][0]).name)
        #print('Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.')

        self.sr = SourceReference(citation='Tester, T., TesterToo, T., Testing, testing', status=1)
        self.res = {'status': 'ok', 
                'message-type': 'work-list', 
                'message-version': '1.0.0', 
                'message': {'facets': {}, 'total-results': 2,
                            'items': [
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
        self.empty_res = {'status': 'ok', 'message-type': 'work-list', 'message-version': '1.0.0', 'message': {'facets': {}, 'total-results': 0, 'items': [], 'items-per-page': 2, 'query': {'start-index': 0, 'search-terms': None}}}
       

    def test_check_valid_author(self):
        self.assertEqual(self.check.check_valid_author(self.file), True)
        # Tiedossa etta ei mene lapi

    def test_check_headers(self):
        self.assertEqual(self.check.check_headers(self.file), True)

    def test_check_headers_false(self):
        self.assertEqual(self.check.check_headers(self.false_file), False)
    
    def test_check_author(self):
        self.assertEqual(self.check.check_author(self.file), True)
    
    def test_check_verbatimScientificName(self):
        self.assertEqual(self.check.check_verbatimScientificName(self.file), True)
    
    def test_false_check_verbatimScientificName_four_words(self):
        self.assertEqual(self.check.check_verbatimScientificName(self.false_file), False)

    def test_false_check_verbatimScientificName_three_words(self):
        self.assertEqual(self.check.check_verbatimScientificName(self.false_file2), False)

    def test_false_check_verbatimScientificName_two_words(self):
        self.assertEqual(self.check.check_verbatimScientificName(self.false_vsn), False)
    
    def test_check_taxonRank(self):
        self.assertEqual(self.check.check_taxonRank(self.file), True)
    
    def test_false_taxonRank(self):
        self.assertEqual(self.check.check_taxonRank(self.false_file), False)
    
    def test_check_sequence(self):
        self.assertEqual(self.check.check_sequence(self.file), True)
    
    def test_false_check_sequence_one_in_wrong_place(self):
        self.assertEqual(self.check.check_sequence(self.false_file2), False)
    
    def test_false_check_sequence_wrong_number(self):
        self.assertEqual(self.check.check_sequence(self.false_sequence), False)
    
    def test_false_check_sequence_not_numeric(self):
        self.assertEqual(self.check.check_sequence(self.false_vsn), False)
    
    def test_check_false_measumerementValue_according_to_sequence(self):
        self.assertEqual(self.check.check_sequence(self.false_measurement_value), False)
    
    def test_check_measurmentValue(self):
        self.assertEqual(self.check.check_measurementValue(self.file), True)
    
    def test_false_check_measurementValue(self):
        self.assertEqual(self.check.check_measurementValue(self.false_file), False)
    
    def test_false_check_references(self):
        self.assertEqual(self.check.check_references(self.false_file2), False)

    def test_check_all(self):
        self.assertEqual(self.check.check_all(self.file), True)
        df = pd.DataFrame.from_dict(self.dict)
        self.assertEqual(self.check.check_all(df), True)

    def test_check_all_wrong_headers(self):
        df = pd.DataFrame.from_dict({'kirjlaia': ['1111-1111-2222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'moi'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })
        self.assertEqual(self.check.check_all(df), False)

    def test_check_all_wrong_author(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'moi'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })
        self.assertEqual(self.check.check_all(df), False)

    def test_check_all_missing_werbatim_scientificname(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':["a a a a", 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'moi'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })
        self.assertEqual(self.check.check_all(df), False)

    def test_check_all_wrong_taxonrank(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['laji', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'moi'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })
        print(self.check.check_all(df))
        self.assertEqual(self.check.check_all(df), False)

    def test_check_all_wrong_sequence(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'moi'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000']})
        self.assertEqual(self.check.check_all(df), False)

    def test_check_all_wrong_measurement_value(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '1111-1111-2222-2233',], 
        'verbatimScientificName':['kapistelifa', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'hello'],
        'sequence':[1,1],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'], 'measurementValue':[0,1] })
        self.assertEqual(self.check.check_all(df), False)

    def test_check_all_wrong_reference(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '1111-1111-2222-2233',], 
        'verbatimScientificName':['kapistelifa', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'hello'],
        'sequence':[1,1],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. '], 'measurementValue':[1,1] })
        self.assertEqual(self.check.check_all(df), False)
    
    def test_check_author_not_a_number(self):
        df = pd.DataFrame.from_dict({'author': ['pena-pena-pena-pena', '1111-1111-2222-2233',], 
        'verbatimScientificName':['kapistelifa', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'hello'],
        'sequence':[1,1],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'] })
        self.assertEqual(self.check.check_author(df), False)

    def test_check_verbatiscientificname_is_empty(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '1111-1111-2222-2233'], 
        'verbatimScientificName':['kapistelija',None], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'hello'],
        'sequence':[1,1],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'] })
        self.assertEqual(self.check.check_verbatimScientificName(df), False)

    def test_check_sequence_scientificnames_dont_mach(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '1111-1111-2222-2222'], 
        'verbatimScientificName':['pena', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'gei'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })
        self.assertEqual(self.check.check_sequence(df), False)

    def test_check_sequence_references_dont_mach(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '1111-1111-2222-2222'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'gei'],
        'sequence':[1,2],
        'references':['tosi  tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })
        self.assertEqual(self.check.check_sequence(df), False)

    def test_new_get_sourcereference_citation(self):
        self.assertEqual(tools.get_sourcereference_citation(self.file.loc[:, 'references'][0], self.user).citation, 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.')

    def test_new_get_entityclass(self):
        self.assertEqual(tools.get_entityclass(self.file.loc[:, 'taxonRank'][0], self.user).name, 'Species')

    def test_existing_entityclass(self):
        self.assertEqual(tools.get_entityclass(self.entity, self.user).name, 'Species')

    def test_new_get_sourceentity(self):
        vs_name = self.file.loc[:, 'verbatimScientificName'][0]
        reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][0], self.user)
        entityclass = tools.get_entityclass(self.file.loc[:, 'taxonRank'][0], self.user)
        self.assertEqual(tools.get_sourceentity(vs_name, reference, entityclass, self.user).name, 'Lagothrix flavicauda')
    
    def test_new_get_timeperiod(self):
       reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][2], self.user)
       self.assertEqual(tools.get_timeperiod(self.file.loc[:, 'samplingEffort'][2], reference, self.user).name, '15-month-study')
    
    def test_new_get_sourcemethod(self):
       reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][3], self.user)
       self.assertEqual(tools.get_sourcemethod(self.file.loc[:, 'measurementMethod'][3], reference, self.user).name, 'observations of fruit consumption')
    
    def test_new_get_sourcelocation(self):
       reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][4], self.user)
       self.assertEqual(tools.get_sourcelocation(self.file.loc[:, 'verbatimLocality'][4], reference, self.user).name, 'Mandu Mandu Gorge, Cape Range National Park, Western Australia')        

    def test_nan_to_zero_empty(self):
        self.assertEqual(tools.possible_nan_to_zero(self.file.loc[:, 'individualCount'][4]), 108)

    def test_nan_to_zero(self):
        self.assertEqual(tools.possible_nan_to_zero(self.file.loc[:, 'individualCount'][0]), 0)
    
    def test_nan_to_none_empty(self):
        self.assertEqual(tools.possible_nan_to_none(self.file.loc[:, 'verbatimEventDate'][0]), None)

    def test_nan_to_nan(self):
        self.assertEqual(tools.possible_nan_to_none(self.file.loc[:, 'verbatimEventDate'][2]), 'October 2009-June 2010 and August 2010-February 2011')

    def test_trims_whitespace(self):
        df = pd.DataFrame.from_dict({'author': ['    1111-1111-2222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':['kapistelija', 'kapistelija    '], 
        'taxonRank':['genus', 'genus'],
        'references':['tosi tieteellinen tutkimus    tm. 2000', 'tosi tieteellinen tutkimus tm.'] })
        tools.trim_df(df)
        self.assertEqual(df.at[0, 'author'],'1111-1111-2222-2222' )
        self.assertEqual(df.at[1, 'verbatimScientificName'],'kapistelija' )
        self.assertEqual(df.at[0, 'references'],'tosi tieteellinen tutkimus tm. 2000' )

    def test_create_masterreference(self):
        answer = tools.create_masterreference('Tester, T., TesterToo, T., Testing, testing', self.res, self.sr, self.user)
        self.assertEquals(answer, True)

    def test_create_masterreference_with_wrong_title(self):
        answer = tools.create_masterreference('Tester, T., TesterToo, T., Testing, not testing at all', self.res, self.sr, self.user)
        self.assertEquals(answer, False)

    def test_create_masterreference_empty(self):
        answer = tools.create_masterreference('Tester, T., TesterToo, T., Testing, testing', self.empty_res, self.sr, self.user)
        self.assertEquals(answer, False)

    def test_title_matches_citation_correct(self):
        answer = tools.title_matches_citation('<i>This is a correct title</i>', 'This is a correct title')
        self.assertEquals(answer, True)
    
    def test_title_matches_citation_false(self):
        answer = tools.title_matches_citation('This is not a correct title', 'This is a correct title')
        self.assertEquals(answer, False)

    def test_make_harvard_citation_journalarticle(self):
        test_citation = tools.make_harvard_citation_journalarticle('Testing, testing', 'doi123', ['Tester, T.', 'TesterToo, T.', 'TesterThree, T.'],
                                                                        '2022', 'Testing container-title', '20', '2', '123-321')
        self.assertEquals('Tester, T., TesterToo, T., TesterThree, T. 2022. Testing, testing. Testing container-title. 20(2), pp.123-321. Available at: doi123.', test_citation)


