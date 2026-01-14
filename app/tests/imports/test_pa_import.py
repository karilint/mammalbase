from types import SimpleNamespace
from unittest.mock import patch

from allauth.socialaccount.models import SocialAccount
from django.test import TestCase
from django.contrib.auth import get_user_model

from imports.importers.proximate_analysis_importer import ProximateAnalysisImporter
from mb.models import ProximateAnalysis
from middleware.current_user import _user

User = get_user_model()


class PAImportTestCase(TestCase):
    def setUp(self):
        self.author_uid = '0000-0000-0000-0000'
        self.user = User.objects.create_user(username='testuser', password='testpass')
        SocialAccount.objects.create(
            user=self.user,
            provider='orcid',
            uid=self.author_uid
        )
        _user.value = self.user
        self.importer = ProximateAnalysisImporter()

    def _row(self, **overrides):
        data = {
            'author': self.author_uid,
            'references': 'Test reference',
            'measurementMethod': 'Dry matter analysis',
            'verbatimLocality': 'Test locality',
            'associatedReferences': 'Ref 1',
            'verbatimEventDate': '2024-01-15',
        }
        data.update(overrides)
        return SimpleNamespace(**data)

    @patch.object(ProximateAnalysisImporter, 'get_or_create_master_reference', return_value=None)
    def test_import_row_creates_proximate_analysis(self, mock_master_reference):
        created = self.importer.importRow(self._row())
        self.assertTrue(created)
        self.assertEqual(ProximateAnalysis.objects.count(), 1)
