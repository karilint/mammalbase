import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from imports.validation_lib.ets_validation import Ets_validation
from recode_extraction.mappers import EtsMapper
from recode_extraction.models import SourceDocument, SourceExtractionRun
from recode_extraction.services.extraction import EvidenceSpan, ExtractedAssertion


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class EtsMapperTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='ets-user',
            email='ets@example.com',
            password='test-pass',
        )
        self.source_document = SourceDocument.objects.create(
            pdf_file=SimpleUploadedFile('ets.pdf', b'%PDF-1.4\ncontent', content_type='application/pdf'),
            title='ETS Source',
            uploader=self.user,
        )
        self.run = SourceExtractionRun.objects.create(
            source=self.source_document,
            status=SourceExtractionRun.Status.COMPLETED,
        )

    def test_maps_assertions_to_ets_records_that_validate(self):
        mapper = EtsMapper()
        assertions = [
            ExtractedAssertion(
                subject_taxon='Canis lupus',
                trait_name='body mass',
                value='12-14',
                unit='kg',
                context='Canis lupus body mass is 12-14 kg.',
                confidence=0.82,
                evidence_spans=[EvidenceSpan(start=0, end=33)],
            ),
            ExtractedAssertion(
                subject_taxon='Canis lupus',
                trait_name='adult mass',
                value='13 ± 1',
                unit='kg',
                context='Adult mass 13 ± 1 kg.',
                confidence=0.76,
                evidence_spans=[EvidenceSpan(start=0, end=20)],
            ),
        ]

        mapping = mapper.map_assertions(
            assertions,
            source_document=self.source_document,
            extraction_run=self.run,
            default_reference='Doe 2024 Mammal Journal',
            default_author='0000-0000-0000-0000',
            page_number=2,
        )

        self.assertEqual(len(mapping.records), 2)
        self.assertEqual(mapping.unmapped_traits, [])

        validator = Ets_validation()
        for record in mapping.records:
            errors = validator.validate(record, validator.rules)
            self.assertEqual(errors, [], msg=f'Validation errors for record: {errors}')
            self.assertEqual(record['source_document_id'], self.source_document.pk)
            self.assertEqual(record['source_extraction_run_id'], self.run.pk)
            self.assertEqual(record['evidence_page_number'], 2)
            self.assertTrue(record['traitID'].startswith('MB:TRAIT:'))

    def test_unmapped_and_invalid_numeric_are_reported(self):
        mapper = EtsMapper()
        assertions = [
            ExtractedAssertion(
                subject_taxon='Canis lupus',
                trait_name='unknown trait',
                value='12',
                unit='kg',
                context='Unknown trait value.',
                confidence=0.4,
                evidence_spans=[],
            ),
            ExtractedAssertion(
                subject_taxon='Canis lupus',
                trait_name='body mass',
                value='not-a-number',
                unit='kg',
                context='Body mass not-a-number kg.',
                confidence=0.2,
                evidence_spans=[],
            ),
        ]

        mapping = mapper.map_assertions(
            assertions,
            source_document=self.source_document,
            extraction_run=self.run,
            default_reference='Doe 2024 Mammal Journal',
            default_author='0000-0000-0000-0000',
            page_number=1,
        )

        self.assertEqual(len(mapping.records), 0)
        self.assertEqual(len(mapping.unmapped_traits), 2)
        reasons = [item.reason for item in mapping.unmapped_traits]
        self.assertTrue(any('unmapped trait_name' in item for item in reasons))
        self.assertTrue(any('invalid numeric value' in item for item in reasons))
