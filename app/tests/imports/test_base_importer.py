from django.test import TestCase
from mb.models.models import EntityRelation
import requests_mock
from imports.importers.base_importer import BaseImporter
from django.contrib.auth.models import User
from .utils.mock_api import generate_mock_api
from allauth.socialaccount.models import SocialAccount
from django.test import Client

class BaseImporterTest(TestCase):
    @requests_mock.Mocker()
    def setUp(self, mock_api):
        generate_mock_api(mock_api)
        self.test_author = User.objects.create_superuser(username='Testi')
        self.social_account = SocialAccount.objects.create(uid='1111-1111-2222-222X', user_id=self.test_author.pk)
        client = Client()
        client.force_login(self.test_author)
        self.base_importer = BaseImporter()
    def test_get_author_when_exist(self):
        #create user
        #get author
        author = self.base_importer.get_author('1111-1111-2222-222X')
        
        #assert Exception
        self.assertEqual(author, self.test_author)
    def test_get_author_when_not_exist(self):
        #assert Exception
        self.assertRaises(Exception, self.base_importer.get_author, 'test')
        

    def test_get_or_create_source_reference_when_new_source(self):
        #create
        source_reference = self.base_importer.get_or_create_source_reference('test', self.test_author)
        #assert
        self.assertEqual(source_reference.citation, 'test')
        
    def test_get_or_create_source_reference_when_exist(self):
        #create
        source_reference = self.base_importer.get_or_create_source_reference('test', self.test_author)
        #get
        source_reference2 = self.base_importer.get_or_create_source_reference('test', self.test_author)
        #assert
        self.assertEqual(source_reference, source_reference2)
        
    def test_get_or_create_entity_class_when_new_entity_class(self):
        #create
        entity_class = self.base_importer.get_or_create_entity_class('test', self.test_author)
        #assert
        self.assertEqual(entity_class.name, 'test')
        
    def test_get_or_create_entity_class_when_exist(self):
        #create
        entity_class = self.base_importer.get_or_create_entity_class('test', self.test_author)
        #get
        entity_class2 = self.base_importer.get_or_create_entity_class('test', self.test_author)
        #assert
        self.assertEqual(entity_class, entity_class2)
        
    def test_get_or_create_source_entity_when_new_entity(self):
        source_reference = self.base_importer.get_or_create_source_reference('test', self.test_author)
        entity_class = self.base_importer.get_or_create_entity_class('test', self.test_author)
        #create
        source_entity = self.base_importer.get_or_create_source_entity('Mangifera', source_reference, entity_class, self.test_author)
        #assert
        self.assertEqual(source_entity.name, 'Mangifera')
        #new enityty relation is created
        
    def test_get_or_create_source_entity_when_exist(self):
        source_reference = self.base_importer.get_or_create_source_reference('test', self.test_author)
        entity_class = self.base_importer.get_or_create_entity_class('test', self.test_author)
        #create
        source_entity = self.base_importer.get_or_create_source_entity('Mangifera', source_reference, entity_class, self.test_author)
        #get
        source_entity2 = self.base_importer.get_or_create_source_entity('Mangifera', source_reference, entity_class, self.test_author)
        #assert
        self.assertEqual(source_entity, source_entity2)
        
    def test_create_entity_relation(self):
        source_reference = self.base_importer.get_or_create_source_reference('test', self.test_author)
        entity_class = self.base_importer.get_or_create_entity_class('test', self.test_author)
        source_entity = self.base_importer.get_or_create_source_entity('Mangifera', source_reference, entity_class, self.test_author)
        #create
        self.base_importer.create_entity_relation(source_entity)
        #get entity relation
        entity_relation = EntityRelation.objects.filter(source_entity=source_entity)
        if len(entity_relation) == 0:
            self.fail('Entity relation not created')
        #assert
        entity_relation[0]
        self.assertEqual(entity_relation.source_entity, source_entity)
        
    def test_create_and_link_entity_relation(self):
        source_reference = self.base_importer.get_or_create_source_reference('test', self.test_author)
        entity_class = self.base_importer.get_or_create_entity_class('test', self.test_author)
        source_entity = self.base_importer.get_or_create_source_entity('Mangifera', source_reference, entity_class, self.test_author)
        #create
        self.base_importer.create_and_link_entity_relation_from_api(source_entity)
        #get entity relation
        entity_relation = EntityRelation.objects.filter(source_entity=source_entity)
        if len(entity_relation) == 0:
            self.fail('Entity relation not created')
        #assert
        entity_relation = entity_relation[0]
        self.assertEqual(entity_relation.source_entity, source_entity)
    
    def test_get_or_create_master_reference_when_new(self):
        #create
        master_reference = self.base_importer.get_or_create_master_reference('Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.', self.test_author)
        #assert
        self.assertEqual(master_reference.citation, 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.')
        
    def test_get_or_create_master_reference_when_exist(self):
        #create
        master_reference = self.base_importer.get_or_create_master_reference('Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.', self.test_author)
        #get
        master_reference2 = self.base_importer.get_or_create_master_reference('Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.', self.test_author)
        #assert
        self.assertEqual(master_reference, master_reference2)
        
    def test_get_or_create_source_location_when_new(self):
        source_reference = self.base_importer.get_or_create_source_reference('test', self.test_author)
        #create
        source_location = self.base_importer.get_or_create_source_location('test',  source_reference, self.test_author)
        #assert
        self.assertEqual(source_location.name, 'test')
        
    def test_get_or_create_source_location_when_exist(self):
        source_reference = self.base_importer.get_or_create_source_reference('test', self.test_author)
        #create
        source_location = self.base_importer.get_or_create_source_location('test',  source_reference, self.test_author)
        #get
        source_location2 = self.base_importer.get_or_create_source_location('test',  source_reference, self.test_author)
        #assert
        self.assertEqual(source_location, source_location2)
        
    def test_get_or_create_time_period_when_new(self):
        source_reference = self.base_importer.get_or_create_source_reference('test', self.test_author)
        #create
        time_period = self.base_importer.get_or_create_time_period('test',  source_reference, self.test_author)
        #assert
        self.assertEqual(time_period.name, 'test')
        
    def test_get_or_create_time_period_when_exist(self):
        source_reference = self.base_importer.get_or_create_source_reference('test', self.test_author)
        #create
        time_period = self.base_importer.get_or_create_time_period('test',  source_reference, self.test_author)
        #get
        time_period2 = self.base_importer.get_or_create_time_period('test',  source_reference, self.test_author)
        #assert
        self.assertEqual(time_period, time_period2)
        
    