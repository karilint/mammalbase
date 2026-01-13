from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import Observation, Location, Species
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
import json
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from middleware.current_user import _user


User = get_user_model()

class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        # Add necessary permissions
        content_type = ContentType.objects.get_for_model(Observation)
        permissions = Permission.objects.filter(content_type=content_type)
        self.user.user_permissions.add(*permissions)
        
        self.location = Location.objects.create(
            name='Test Location',
            latitude=60.1695,
            longitude=24.9354
        )
        self.species = Species.objects.create(name='Test Species')
        self.client.force_login(self.user)
        _user.value = self.user

    def create_test_image(self):
        """Helper method to create a test image file"""
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'PNG')
        file.seek(0)
        return SimpleUploadedFile('test.png', file.read(), content_type='image/png')


class ObservationListViewTest(BaseTestCase):
    def test_list_view_status(self):
        response = self.client.get(reverse('observation_list'))
        self.assertEqual(response.status_code, 200)

    def test_list_view_template(self):
        response = self.client.get(reverse('observation_list'))
        self.assertTemplateUsed(response, 'app/observation_list.html')

    def test_list_view_contains_observations(self):
        observation = Observation.objects.create(
            location=self.location,
            species=self.species,
            observation_date=datetime.now(timezone.utc),
            notes='Test observation',
            observer=self.user
        )
        response = self.client.get(reverse('observation_list'))
        self.assertContains(response, 'Test observation')


class ObservationDetailViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.observation = Observation.objects.create(
            location=self.location,
            species=self.species,
            observation_date=datetime.now(timezone.utc),
            notes='Test observation',
            observer=self.user
        )

    def test_detail_view_status(self):
        response = self.client.get(
            reverse('observation_detail', kwargs={'pk': self.observation.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_detail_view_template(self):
        response = self.client.get(
            reverse('observation_detail', kwargs={'pk': self.observation.pk})
        )
        self.assertTemplateUsed(response, 'app/observation_detail.html')

    def test_detail_view_contains_observation_data(self):
        response = self.client.get(
            reverse('observation_detail', kwargs={'pk': self.observation.pk})
        )
        self.assertContains(response, 'Test observation')
        self.assertContains(response, 'Test Location')
        self.assertContains(response, 'Test Species')


class ObservationCreateViewTest(BaseTestCase):
    def test_create_view_status(self):
        response = self.client.get(reverse('observation_create'))
        self.assertEqual(response.status_code, 200)

    def test_create_view_template(self):
        response = self.client.get(reverse('observation_create'))
        self.assertTemplateUsed(response, 'app/observation_form.html')

    @patch('app.views.get_weather_data')
    def test_create_observation_with_weather(self, mock_weather):
        mock_weather.return_value = {
            'temperature': 20.5,
            'description': 'Clear sky'
        }
        
        response = self.client.post(reverse('observation_create'), {
            'location': self.location.id,
            'species': self.species.id,
            'observation_date': '2024-01-15 10:00:00',
            'notes': 'New observation'
        })
        
        self.assertEqual(response.status_code, 302)
        observation = Observation.objects.latest('id')
        self.assertEqual(observation.notes, 'New observation')
        mock_weather.assert_called_once()

    def test_create_observation_with_image(self):
        test_image = self.create_test_image()
        
        response = self.client.post(reverse('observation_create'), {
            'location': self.location.id,
            'species': self.species.id,
            'observation_date': '2024-01-15 10:00:00',
            'notes': 'Observation with image',
            'image': test_image
        })
        
        self.assertEqual(response.status_code, 302)
        observation = Observation.objects.latest('id')
        self.assertTrue(observation.image)


class ObservationUpdateViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.observation = Observation.objects.create(
            location=self.location,
            species=self.species,
            observation_date=datetime.now(timezone.utc),
            notes='Original notes',
            observer=self.user
        )

    def test_update_view_status(self):
        response = self.client.get(
            reverse('observation_update', kwargs={'pk': self.observation.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_update_observation(self):
        response = self.client.post(
            reverse('observation_update', kwargs={'pk': self.observation.pk}),
            {
                'location': self.location.id,
                'species': self.species.id,
                'observation_date': '2024-01-15 10:00:00',
                'notes': 'Updated notes'
            }
        )
        
        self.assertEqual(response.status_code, 302)
        self.observation.refresh_from_db()
        self.assertEqual(self.observation.notes, 'Updated notes')


class ObservationDeleteViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.observation = Observation.objects.create(
            location=self.location,
            species=self.species,
            observation_date=datetime.now(timezone.utc),
            notes='To be deleted',
            observer=self.user
        )

    def test_delete_view_status(self):
        response = self.client.get(
            reverse('observation_delete', kwargs={'pk': self.observation.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_observation(self):
        observation_id = self.observation.pk
        response = self.client.post(
            reverse('observation_delete', kwargs={'pk': observation_id})
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Observation.objects.filter(pk=observation_id).exists())


class WeatherAPITest(BaseTestCase):
    @patch('app.views.requests.get')
    def test_weather_api_call(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'main': {'temp': 20.5},
            'weather': [{'description': 'Clear sky'}]
        }
        mock_get.return_value = mock_response

        from app.views import get_weather_data
        weather_data = get_weather_data(60.1695, 24.9354)

        self.assertEqual(weather_data['temperature'], 20.5)
        self.assertEqual(weather_data['description'], 'Clear sky')

    @patch('app.views.requests.get')
    def test_weather_api_failure(self, mock_get):
        mock_get.side_effect = Exception('API Error')

        from app.views import get_weather_data
        weather_data = get_weather_data(60.1695, 24.9354)

        self.assertIsNone(weather_data)
