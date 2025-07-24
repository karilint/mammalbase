from django.urls import reverse
from django.test import TestCase
import requests_mock

from .services import BASE_TGN_URL


class TgnSearchTests(TestCase):
    @requests_mock.Mocker()
    def test_search_place_handles_network_error(self, mocker):
        mocker.get(BASE_TGN_URL, status_code=403, text='Forbidden')
        url = reverse('tgn_search')
        response = self.client.get(url, {'name': 'Amboseli'})
        self.assertEqual(response.status_code, 502)
        self.assertIn('Failed to query Getty TGN', response.json()['error'])

