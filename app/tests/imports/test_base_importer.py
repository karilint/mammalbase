from django.test import TestCase
from mb.models import EntityRelation
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
        
    