from django.test import TestCase
from django.contrib.auth import get_user_model
from middleware.current_user import _user
from app.models import Project, Location, Survey, Deployment, Camera, MediaFile
from app.imports.pa_import import PAImporter
import json
import os

User = get_user_model()


class PAImportTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(self.user)
        _user.value = self.user
        
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user
        )
        
        # Load test data
        test_data_path = os.path.join(os.path.dirname(__file__), 'test_data', 'pa_test_data.json')
        with open(test_data_path, 'r') as f:
            self.test_data = json.load(f)
    
    def test_import_locations(self):
        importer = PAImporter(self.project, self.test_data)
        importer.import_locations()
        
        self.assertEqual(Location.objects.filter(project=self.project).count(), 2)
        location = Location.objects.get(name='Location 1')
        self.assertEqual(location.latitude, 60.1234)
        self.assertEqual(location.longitude, 24.5678)
    
    def test_import_surveys(self):
        importer = PAImporter(self.project, self.test_data)
        importer.import_locations()
        importer.import_surveys()
        
        self.assertEqual(Survey.objects.filter(project=self.project).count(), 1)
        survey = Survey.objects.get(name='Survey 1')
        self.assertIsNotNone(survey.start_date)
    
    def test_import_deployments(self):
        importer = PAImporter(self.project, self.test_data)
        importer.import_locations()
        importer.import_surveys()
        importer.import_deployments()
        
        self.assertEqual(Deployment.objects.filter(survey__project=self.project).count(), 2)
        deployment = Deployment.objects.first()
        self.assertIsNotNone(deployment.location)
        self.assertIsNotNone(deployment.survey)
    
    def test_full_import(self):
        importer = PAImporter(self.project, self.test_data)
        result = importer.run_import()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['locations_imported'], 2)
        self.assertEqual(result['surveys_imported'], 1)
        self.assertEqual(result['deployments_imported'], 2)
