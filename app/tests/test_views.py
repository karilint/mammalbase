from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
import tempfile, csv, os
from allauth.socialaccount.models import SocialAccount
import imports.views as views
import pandas as pd
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from allauth.socialaccount.models import SocialAccount
from mb.models.models import EntityClass, MasterReference, SourceAttribute, SourceEntity, SourceLocation, SourceMethod, SourceReference, SourceStatistic, TimePeriod, DietSet, FoodItem, DietSetItem, TaxonomicUnits, ChoiceValue, MasterEntity
from itis.models import Kingdom, TaxonUnitTypes
from imports.tools import Check
import imports.tools as tools
import tempfile, csv, os
import pandas as pd
import json
import requests_mock


class ImportViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(username='Testi')
        self.client.force_login(self.user)
        self.accountuser = SocialAccount.objects.create(uid='1111-1111-2222-222X', user_id=self.user.pk)
        self.reference1 = SourceReference.objects.create(citation='Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.')
        self.reference2 = SourceReference.objects.create(citation='Creese, S., Davies, S.J. and Bowen, B.J., 2019. Comparative dietary analysis of the black-flanked rock-wallaby (Petrogale lateralis lateralis), the euro (Macropus robustus erubescens) and the feral goat (Capra hircus) from Cape Range National Park, Western Australia. Australian Mammalogy, 41(2), pp.220-230.')
        #self.user = User.objects.create_user('testi', 'testi@jotain.com', '1234')
        #self.client.login(username='testi', password='1234')
    def generate_mock_api(self, m):
        url_dict = {
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Lagothrix%20flavicauda':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"(Humboldt, 1812)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["Yellow-tailed Woolly Monkey","Peruvian Yellow-tailed Woolly Monkey"],"nameUsage":"valid","scientificName":"Lagothrix flavicauda","tsn":"572961"}],"requestedName":"Lagothrix flavicauda"}',
            'https://www.itis.gov/ITISWebService/jsonservice/getFullHierarchyFromTSN?tsn=572961':'{"author":"","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecordList","hierarchyList":[{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"","parentTsn":"","rankName":"Kingdom","taxonName":"Animalia","tsn":"202423"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Animalia","parentTsn":"202423","rankName":"Subkingdom","taxonName":"Bilateria","tsn":"914154"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Bilateria","parentTsn":"914154","rankName":"Infrakingdom","taxonName":"Deuterostomia","tsn":"914156"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Deuterostomia","parentTsn":"914156","rankName":"Phylum","taxonName":"Chordata","tsn":"158852"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Chordata","parentTsn":"158852","rankName":"Subphylum","taxonName":"Vertebrata","tsn":"331030"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Vertebrata","parentTsn":"331030","rankName":"Infraphylum","taxonName":"Gnathostomata","tsn":"914179"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Gnathostomata","parentTsn":"914179","rankName":"Superclass","taxonName":"Tetrapoda","tsn":"914181"},{"author":"Linnaeus, 1758","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Tetrapoda","parentTsn":"914181","rankName":"Class","taxonName":"Mammalia","tsn":"179913"},{"author":"Parker and Haswell, 1897","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Mammalia","parentTsn":"179913","rankName":"Subclass","taxonName":"Theria","tsn":"179916"},{"author":"Gill, 1872","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Theria","parentTsn":"179916","rankName":"Infraclass","taxonName":"Eutheria","tsn":"179925"},{"author":"Linnaeus, 1758","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Eutheria","parentTsn":"179925","rankName":"Order","taxonName":"Primates","tsn":"180089"},{"author":"Pocock, 1918","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Primates","parentTsn":"180089","rankName":"Suborder","taxonName":"Haplorrhini","tsn":"943773"},{"author":"Haeckel, 1866","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Haplorrhini","parentTsn":"943773","rankName":"Infraorder","taxonName":"Simiiformes","tsn":"943778"},{"author":"Gray, 1825","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Simiiformes","parentTsn":"943778","rankName":"Family","taxonName":"Atelidae","tsn":"943785"},{"author":"Gray, 1825","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Atelidae","parentTsn":"943785","rankName":"Subfamily","taxonName":"Atelinae","tsn":"572780"},{"author":"É. Geoffroy Saint-Hilaire in Humboldt, 1812","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Atelinae","parentTsn":"572780","rankName":"Genus","taxonName":"Lagothrix","tsn":"572814"},{"author":"(Humboldt, 1812)","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Lagothrix","parentTsn":"572814","rankName":"Species","taxonName":"Lagothrix flavicauda","tsn":"572961"}],"rankName":"","sciName":"","tsn":"572961"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Capra%20hircus':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"Linnaeus, 1758","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["goat (feral)","domestic goat","Goat"],"nameUsage":"valid","scientificName":"Capra hircus","tsn":"180715"},{"author":"Linnaeus, 1758","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Capra hircus hircus","tsn":"898773"},{"author":"Erxleben, 1777","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["bezoar"],"nameUsage":"valid","scientificName":"Capra hircus aegagrus","tsn":"898774"},{"author":"Lydekker, 1913","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Capra hircus chialtanensis","tsn":"898775"},{"author":"Schinz, 1838","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Capra hircus cretica","tsn":"898776"},{"author":"Ivrea, 1899","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Capra hircus jourensis","tsn":"898777"},{"author":"(Erhard, 1858)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Capra hircus picta","tsn":"898778"}],"requestedName":"Capra hircus"}',
            'https://www.itis.gov/ITISWebService/jsonservice/getFullHierarchyFromTSN?tsn=180715':'{"author":"","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecordList","hierarchyList":[{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"","parentTsn":"","rankName":"Kingdom","taxonName":"Animalia","tsn":"202423"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Animalia","parentTsn":"202423","rankName":"Subkingdom","taxonName":"Bilateria","tsn":"914154"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Bilateria","parentTsn":"914154","rankName":"Infrakingdom","taxonName":"Deuterostomia","tsn":"914156"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Deuterostomia","parentTsn":"914156","rankName":"Phylum","taxonName":"Chordata","tsn":"158852"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Chordata","parentTsn":"158852","rankName":"Subphylum","taxonName":"Vertebrata","tsn":"331030"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Vertebrata","parentTsn":"331030","rankName":"Infraphylum","taxonName":"Gnathostomata","tsn":"914179"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Gnathostomata","parentTsn":"914179","rankName":"Superclass","taxonName":"Tetrapoda","tsn":"914181"},{"author":"Linnaeus, 1758","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Tetrapoda","parentTsn":"914181","rankName":"Class","taxonName":"Mammalia","tsn":"179913"},{"author":"Parker and Haswell, 1897","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Mammalia","parentTsn":"179913","rankName":"Subclass","taxonName":"Theria","tsn":"179916"},{"author":"Gill, 1872","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Theria","parentTsn":"179916","rankName":"Infraclass","taxonName":"Eutheria","tsn":"179925"},{"author":"Owen, 1848","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Eutheria","parentTsn":"179925","rankName":"Order","taxonName":"Artiodactyla","tsn":"180692"},{"author":"Gray, 1821","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Artiodactyla","parentTsn":"180692","rankName":"Family","taxonName":"Bovidae","tsn":"180704"},{"author":"Gray, 1821","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Bovidae","parentTsn":"180704","rankName":"Subfamily","taxonName":"Caprinae","tsn":"552327"},{"author":"Linnaeus, 1758","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Caprinae","parentTsn":"552327","rankName":"Genus","taxonName":"Capra","tsn":"180714"},{"author":"Linnaeus, 1758","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Capra","parentTsn":"180714","rankName":"Species","taxonName":"Capra hircus","tsn":"180715"},{"author":"Erxleben, 1777","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Capra hircus","parentTsn":"180715","rankName":"Subspecies","taxonName":"Capra hircus aegagrus","tsn":"898774"},{"author":"Lydekker, 1913","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Capra hircus","parentTsn":"180715","rankName":"Subspecies","taxonName":"Capra hircus chialtanensis","tsn":"898775"},{"author":"Schinz, 1838","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Capra hircus","parentTsn":"180715","rankName":"Subspecies","taxonName":"Capra hircus cretica","tsn":"898776"},{"author":"Linnaeus, 1758","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Capra hircus","parentTsn":"180715","rankName":"Subspecies","taxonName":"Capra hircus hircus","tsn":"898773"},{"author":"Ivrea, 1899","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Capra hircus","parentTsn":"180715","rankName":"Subspecies","taxonName":"Capra hircus jourensis","tsn":"898777"},{"author":"(Erhard, 1858)","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Capra hircus","parentTsn":"180715","rankName":"Subspecies","taxonName":"Capra hircus picta","tsn":"898778"}],"rankName":"","sciName":"","tsn":"180715"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Primarily':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[null],"requestedName":"Primarily"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Primarily%20frugivorous':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[null],"requestedName":"Primarily frugivorous"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Frugivorous':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[null],"requestedName":"Frugivorous"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Leaves':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"R. T. Moore, 1934","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Chaetocercus heliodor cleavesi","tsn":"693922"},{"author":"Davis, 1930","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Diceroprocta cleavesi","tsn":"846873"}],"requestedName":"Leaves"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Fruit':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"Hook. & Arn.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["downy-fruit buttercup"],"nameUsage":"accepted","scientificName":"Ranunculus hebecarpus","tsn":"18610"},{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["spinyfruit buttercup"],"nameUsage":"accepted","scientificName":"Ranunculus muricatus","tsn":"18629"},{"author":"J.R. Forst. & G. Forst.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["breadfruit"],"nameUsage":"accepted","scientificName":"Artocarpus","tsn":"19071"},{"author":"R.S. Cowan","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["angularfruit ma\'oloa"],"nameUsage":"accepted","scientificName":"Neraudia angulata","tsn":"19174"},{"author":"L.A. Galloway","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["large-fruited sand-verbena","largefruit sand verbena","large-fruited sand verbena"],"nameUsage":"accepted","scientificName":"Abronia macrocarpa","tsn":"19561"},{"author":"Engelm.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["marblefruit pricklypear"],"nameUsage":"accepted","scientificName":"Opuntia strigil","tsn":"19737"},{"author":"(A.E. Porsild) Hult�n","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["largefruit catchfly"],"nameUsage":"not accepted","scientificName":"Silene macrosperma","tsn":"20081"},{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["largefruit amaranth"],"nameUsage":"accepted","scientificName":"Amaranthus deflexus","tsn":"20731"}],"requestedName":"Fruit"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Fruits':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"Schkuhr ex Willd.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["carex à fruits clairsemés"],"nameUsage":"accepted","scientificName":"Carex oligocarpa","tsn":"39728"},{"author":"(Linnaeus, 1758)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["nitidule des fruits"],"nameUsage":"valid","scientificName":"Carpophilus hemipterus","tsn":"114296"},{"author":"(Walker, 1858)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["noctuelle des fruits verts"],"nameUsage":"valid","scientificName":"Lithophane antennata","tsn":"117409"},{"author":"(Meisn.) Arcang.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["renouée à petits fruits"],"nameUsage":"accepted","scientificName":"Polygonum aviculare ssp. depressum","tsn":"823866"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["plantes à fruits"],"nameUsage":"not accepted","scientificName":"Angiospermae","tsn":"846505"}],"requestedName":"Fruits"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Fruits%20ficus':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[null],"requestedName":"Fruits ficus"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Ficus':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"accepted","scientificName":"Ornithocercus magnificus","tsn":"9988"},{"author":"(Hultén) L.D. Benson","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["Pacific buttercup"],"nameUsage":"accepted","scientificName":"Ranunculus pacificus","tsn":"18636"},{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["fig"],"nameUsage":"accepted","scientificName":"Ficus","tsn":"19081"},{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ficus","tsn":"19082"},{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["weeping fig"],"nameUsage":"accepted","scientificName":"Ficus benjamina","tsn":"19083"},{"author":"Urb.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ficus broadwayi","tsn":"19084"},{"author":"Roxb. ex Hornem.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["Indian rubber fig","Indian rubberplant"],"nameUsage":"accepted","scientificName":"Ficus elastica","tsn":"19085"},{"author":"Warb.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ficus grenadensis","tsn":"19086"},{"author":"Warb.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ficus hartii","tsn":"19087"},{"author":"Urb.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ficus tobagensis","tsn":"19088"},{"author":"Warb.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ficus triangularis","tsn":"19089"}],"requestedName":"Ficus"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Unidenti%EF%AC%81ed':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[null],"requestedName":"Unidenti?ed"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Unidenti%EF%AC%81ed%20monocots':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[null],"requestedName":"Unidenti?ed monocots"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Monocots':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["monocots"],"nameUsage":"accepted","scientificName":"Lilianae","tsn":"846542"}],"requestedName":"Monocots"}',

        }
        for url, data in url_dict.items():
            m.get(url, text=data)
    def test_import_diet_set_view(self):
        response = self.client.get('/import/diet_set')
        #print('helo', response.content, 'helo', response.client, response.context)
        self.assertEqual(response.status_code, 200)
    
    def test_import_diet_set_reverse(self):
        response = self.client.get(reverse('import_diet_set'))
        self.assertEqual(response.status_code, 200)
    
    def test_import_post_ds_failing_file(self):
        with open('test_bad.csv', 'w') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(['author', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue',  'references'])
            writer.writerow(['0000-0000-0000-000X', 'Lagothrix flavicauda Lagothrix flavicauda', 'Species', 'primarily frugivorous', '1', '', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            writer.writerow(['0000-0000-0000-000X',	'Lagothrix flavicauda',	'animal',	'leaves', '2', '', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            writer.writerow(['0000-0000-0000-000X',	'Lagothrix flavicauda',	'Species',	'fruit', '1', '46.3','Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
        with open('test_bad.csv', 'r') as fp:
            response = self.client.post('/import/diet_set', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'The author 0000-0000-0000-000X is not a valid ORCID ID at row 2.')
        self.assertEqual(response.status_code, 302)
            
    def test_import_ds_post_wrong_file(self):
        with open('tests/test_tools.py', 'r') as fp:
            response = self.client.post('/import/diet_set', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1) 
        self.assertEqual('Unable to upload file.' in str(messages[0]), True)
        self.assertEqual(response.status_code, 302)
    
    def test_import_ets_post_wrong_file(self):
        with open('tests/test_tools.py', 'r') as fp:
            response = self.client.post('/import/ets', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1) 
        self.assertEqual('Unable to upload file.' in str(messages[0]), True)
        self.assertEqual(response.status_code, 302)

    def test_import_ets_view(self):
        response = self.client.get('/import/ets')
        self.assertEqual(response.status_code, 200)

    def test_import_ets_reverse(self):
        response = self.client.get(reverse('import_ets'))
        self.assertEqual(response.status_code, 200)
    @requests_mock.Mocker()
    def test_import_ds_post(self, m):
        self.generate_mock_api(m)
        with open('test_post.csv', 'w') as file:
            writer = csv.writer(file, delimiter='\t')
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
            writer.writerow(['1111-1111-2222-222X',	'Capra hircus',	'Species', 'Mandu Mandu Gorge, Cape Range National Park, Western Australia', 'Summer (February, March, April and October)', '', '', '108', 'between February and October 2006', 'The percentage of plant species found in scats.', 'Unidentiﬁed monocots', '1','36.8', 'Original study', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.' ])
        with open('test_post.csv', 'r') as fp:
            response = self.client.post('/import/diet_set', {'name': 'fred', 'csv_file': fp, 'force':'force'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual('File imported successfully.' in str(messages[0]), True)
        self.assertEqual(response.status_code, 302)

    def test_import_ets_post(self):
        with open('test_post.csv', 'w') as file:
            writer = csv.writer(file, delimiter='\t')
            #dont maybe copy this file for ets tests, it doesnt have correct headers :D
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
        with open('test_post.csv', 'r') as fp:
            response = self.client.post('/import/ets', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'The import file does not contain the required headers. The missing header is: verbatimTraitName.')
        self.assertEqual(response.status_code, 302) 
    
    def test_tsn_search_get(self):
        response = self.client.get("/tsn/search?query=grasshopper")
        self.assertEqual(response.status_code, 200)
        message = json.loads(str(response.content, encoding="utf8"))
        self.assertNotEqual(message["message"], "Connection to ITIS failed.")
        self.assertNotEqual(message["message"], "Found no entries")
        self.assertTrue("Found" in message["message"] and "entries" in message["message"])
    
    def test_tsn_search_post(self):
        kingdom_id = Kingdom.objects.create(name="Animalia").pk
        rank_id = TaxonUnitTypes.objects.create(rank_name="Species", rank_id=10, dir_parent_rank_id=10, req_parent_rank_id=10, kingdom_id=kingdom_id).pk
        test_data = {
            'author': '(Coues, 1874)',
            'class': 'gov.usgs.itis.itis_service.data.SvcItisTerm',
            'commonNames': ['Southern Grasshopper Mouse'],
            'nameUsage': 'valid',
            'scientificName': 'Onychomys torridus',
            'tsn': '180383'
        }
        response = self.client.post("/tsn/search", {'tsn_data':json.dumps(test_data)})
        self.assertEqual(response.status_code, 201)
        queryset = TaxonomicUnits.objects.filter(tsn="180383")
        self.assertTrue(len(queryset)==1)
        object = queryset[0]
        self.assertEqual(object.tsn, 180383)
        self.assertEqual(object.kingdom_id, kingdom_id)
        self.assertEqual(object.rank_id, rank_id)
        self.assertEqual(object.completename, test_data["scientificName"])
        self.assertTrue("180383" in object.hierarchy_string)
        self.assertTrue("Onychomys torridus" in object.hierarchy)