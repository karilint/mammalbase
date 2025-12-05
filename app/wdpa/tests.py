from django.urls import reverse
from django.test import TestCase
import requests_mock

from .services import BASE_WDPA_SEARCH_URL


class WdpaSearchTests(TestCase):
    @requests_mock.Mocker()
    def test_search_place_handles_network_error(self, mocker):
        mocker.get(BASE_WDPA_SEARCH_URL, status_code=403, text='Forbidden')
        url = reverse('wdpa_search')
        response = self.client.get(url, {'name': 'Amboseli'})
        self.assertEqual(response.status_code, 502)
        self.assertIn('Failed to query Protected Planet', response.json()['error'])
