from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, SimpleTestCase

from matchtools.views import match_location


class MatchLocationTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('matchtools.views.get_hierarchy_chain', return_value=['Asia', 'Nam Et-Phou Louey'])
    @patch('matchtools.views.add_wdpa_location')
    def test_match_location_accepts_country_names_with_apostrophes(self, add_wdpa_location, _get_hierarchy_chain):
        class StubLocation:
            name = 'Nam Et-Phou Louey'

        add_wdpa_location.return_value = [StubLocation()]

        payload = "{'original_name': 'Nam Et-Phou Louey', 'country': 'Lao People\\'s Democratic Republic', 'wdpa_id': '1234'}"
        request = self.factory.post(
            '/matchtools/match_location/',
            data={
                'locationData': payload,
                'sourceLocation': '1',
                'provider': 'wdpa',
            },
        )
        request.user = AnonymousUser()

        response = match_location(request)

        self.assertEqual(response.status_code, 200)
        add_wdpa_location.assert_called_once_with(
            {
                'original_name': 'Nam Et-Phou Louey',
                'country': "Lao People's Democratic Republic",
                'wdpa_id': '1234',
            },
            '1',
            user=request.user,
        )
        self.assertJSONEqual(
            response.content,
            {
                'masterLocation': 'Nam Et-Phou Louey',
                'hierarchy_locations': ['Asia', 'Nam Et-Phou Louey'],
            },
        )
