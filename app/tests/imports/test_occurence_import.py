from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from app.tdwg.models import Taxon, ChoiceValue
from observations.models import Occurrence
from imports.occurrence_import import OccurrenceImporter
from io import StringIO
import csv
from middleware.current_user import _user

User = get_user_model()


class OccurrenceImportTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.test_author = User.objects.create_user(
            username='testauthor',
            password='testpass123'
        )
        self.client.force_login(self.test_author)
        _user.value = self.test_author
        
        # Create test taxon
        self.taxon = Taxon.objects.create(
            scientific_name='Ursus arctos',
            common_name='Brown Bear',
            rank='species'
        )
        
        # Create test choice values
        self.sex_male = ChoiceValue.objects.create(
            field_name='sex',
            value='Male'
        )
        self.sex_female = ChoiceValue.objects.create(
            field_name='sex',
            value='Female'
        )
        self.age_adult = ChoiceValue.objects.create(
            field_name='age_class',
            value='Adult'
        )
        
    def test_import_basic_occurrence(self):
        """Test importing a basic occurrence record"""
        csv_data = StringIO(
            "scientific_name,date,latitude,longitude,observer\n"
            "Ursus arctos,2024-01-15,60.1699,24.9384,John Doe"
        )
        
        importer = OccurrenceImporter()
        results = importer.import_from_csv(csv_data, self.test_author)
        
        self.assertEqual(results['success'], 1)
        self.assertEqual(results['errors'], 0)
        
        occurrence = Occurrence.objects.first()
        self.assertEqual(occurrence.taxon, self.taxon)
        self.assertEqual(occurrence.observer, 'John Doe')
        self.assertEqual(str(occurrence.date), '2024-01-15')
        
    def test_import_with_optional_fields(self):
        """Test importing occurrence with optional fields"""
        csv_data = StringIO(
            "scientific_name,date,latitude,longitude,observer,sex,age_class,count\n"
            "Ursus arctos,2024-01-15,60.1699,24.9384,Jane Smith,Male,Adult,2"
        )
        
        importer = OccurrenceImporter()
        results = importer.import_from_csv(csv_data, self.test_author)
        
        self.assertEqual(results['success'], 1)
        occurrence = Occurrence.objects.first()
        self.assertEqual(occurrence.sex, self.sex_male)
        self.assertEqual(occurrence.age_class, self.age_adult)
        self.assertEqual(occurrence.count, 2)
        
    def test_import_invalid_taxon(self):
        """Test importing with non-existent taxon"""
        csv_data = StringIO(
            "scientific_name,date,latitude,longitude,observer\n"
            "Nonexistent species,2024-01-15,60.1699,24.9384,John Doe"
        )
        
        importer = OccurrenceImporter()
        results = importer.import_from_csv(csv_data, self.test_author)
        
        self.assertEqual(results['success'], 0)
        self.assertEqual(results['errors'], 1)
        self.assertIn('Taxon not found', results['error_details'][0])
        
    def test_import_multiple_records(self):
        """Test importing multiple occurrence records"""
        csv_data = StringIO(
            "scientific_name,date,latitude,longitude,observer\n"
            "Ursus arctos,2024-01-15,60.1699,24.9384,John Doe\n"
            "Ursus arctos,2024-01-16,61.1699,25.9384,Jane Smith"
        )
        
        importer = OccurrenceImporter()
        results = importer.import_from_csv(csv_data, self.test_author)
        
        self.assertEqual(results['success'], 2)
        self.assertEqual(results['errors'], 0)
        self.assertEqual(Occurrence.objects.count(), 2)
