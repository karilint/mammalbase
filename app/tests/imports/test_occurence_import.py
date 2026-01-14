from types import SimpleNamespace
from unittest.mock import patch

from allauth.socialaccount.models import SocialAccount
from django.test import TestCase
from django.contrib.auth import get_user_model

from imports.importers.occurrence_importer import OccurrencesImporter
from mb.models import ChoiceValue, Occurrence
from middleware.current_user import _user

User = get_user_model()


class OccurrenceImportTest(TestCase):
    def setUp(self):
        self.author_uid = '0000-0000-0000-0000'
        self.test_author = User.objects.create_user(
            username='testauthor',
            password='testpass123'
        )
        SocialAccount.objects.create(
            user=self.test_author,
            provider='orcid',
            uid=self.author_uid
        )
        _user.value = self.test_author
        self.importer = OccurrencesImporter()

    def _row(self, **overrides):
        data = {
            'author': self.author_uid,
            'references': 'Test reference',
            'taxonRank': 'Species',
            'verbatimScientificName': 'Ursus arctos',
            'habitatType': 'Forest',
            'habitatPercentage': 50,
            'verbatimLocality': 'Test locality',
            'verbatimElevation': '100',
            'verbatimDepth': '10',
            'verbatimCoordinates': '60.1699, 24.9384',
            'verbatimLatitude': '60.1699',
            'verbatimLongitude': '24.9384',
            'verbatimCoordinateSystem': 'decimal degrees',
            'verbatimSRS': 'WGS84',
            'verbatimEventDate': '2024-01-15',
            'sex': 'male',
            'lifeStage': 'adult',
            'organismQuantity': '2',
            'organismQuantityType': 'individuals',
            'occurrenceRemarks': 'note',
            'associatedReferences': 'ref',
        }
        data.update(overrides)
        return SimpleNamespace(**data)

    @patch.object(OccurrencesImporter, 'create_entity_relation', return_value=None)
    @patch.object(OccurrencesImporter, 'get_or_create_master_reference', return_value=None)
    def test_import_row_creates_occurrence(self, mock_master_reference, mock_entity_relation):
        created = self.importer.importRow(self._row())
        self.assertTrue(created)
        self.assertEqual(Occurrence.objects.count(), 1)
        self.assertTrue(
            ChoiceValue.objects.filter(choice_set='Gender', caption='Male').exists()
        )
