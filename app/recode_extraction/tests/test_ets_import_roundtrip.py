from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from types import SimpleNamespace

from django.test import TestCase

from imports.importers.ets_importer import EtsImporter
from mb.models import SourceAttribute, SourceMeasurementValue
from recode_extraction.mappers.ets import EtsMapper


class EtsImportRoundtripTests(TestCase):
    def test_roundtrip(self):
        user = User.objects.create(username='test')
        SocialAccount.objects.create(user=user, provider='orcid', uid='0000-0000-0000-0000')
        row = EtsMapper().candidate_to_ets(
            {
                'candidate_id': 1,
                'trait_text': 'body mass',
                'value_text': '5',
                'species_text': 'Homo sapiens',
                'unit_text': 'kg',
                'token_ids': ['1-1'],
                'page_number': 1,
                'snippet': 'Homo sapiens body mass 5 kg',
            },
            default_reference='Ref 2024',
            default_author='0000-0000-0000-0000',
            source_document_id=1,
            extraction_run_id=1,
        )
        EtsImporter().importRow(SimpleNamespace(**row))
        assert SourceMeasurementValue.objects.count() == 1
        assert SourceAttribute.objects.filter(name='body mass').exists()
        created = SourceMeasurementValue.objects.first()
        assert 'candidate_id=' in (created.remarks or '')
