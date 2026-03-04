import tempfile
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from recode_extraction.models import (
    ExtractedAssertionModel,
    ExtractedEntity,
    SourceDocument,
    SourceExtractionRun,
)
from recode_extraction.services.runs import create_extraction_run


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class RunPersistenceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='pipeline-user',
            email='pipeline@example.com',
            password='pw-123456',
        )
        self.document = SourceDocument.objects.create(
            pdf_file=SimpleUploadedFile('pipeline.pdf', b'%PDF-1.4\ncontent', content_type='application/pdf'),
            title='Pipeline Source',
            year=2024,
            uploader=self.user,
        )

    @mock.patch('recode_extraction.services.orchestrator.PdfToTextService.extract')
    def test_dry_run_persists_entities_and_assertions_without_ets(self, extract_mock):
        extract_mock.return_value = {
            'pages': [{'page_number': 1, 'text': 'Canis lupus body mass is 12 kg.'}],
            'full_text': 'Canis lupus body mass is 12 kg.',
            'extraction_warnings': [],
            'backend': 'pypdf',
        }

        run = create_extraction_run(self.document, actor_id=self.user.pk, dry_run=True)

        self.assertEqual(run.status, SourceExtractionRun.Status.COMPLETED)
        self.assertEqual(run.parameters.get('dry_run'), True)
        self.assertGreater(ExtractedEntity.objects.filter(extraction_run=run).count(), 0)
        self.assertGreater(ExtractedAssertionModel.objects.filter(extraction_run=run).count(), 0)
        self.assertEqual(
            ExtractedAssertionModel.objects.filter(extraction_run=run, ets_persisted=True).count(),
            0,
        )

    @mock.patch('recode_extraction.services.orchestrator.PdfToTextService.extract')
    @mock.patch('recode_extraction.services.orchestrator.RecodePipelineRunner._persist_single_ets_record')
    def test_ets_persistence_failure_marks_run_failed_without_partial_flags(self, persist_mock, extract_mock):
        extract_mock.return_value = {
            'pages': [{'page_number': 1, 'text': 'Canis lupus body mass is 12 kg. Adult mass was 10 kg.'}],
            'full_text': 'Canis lupus body mass is 12 kg. Adult mass was 10 kg.',
            'extraction_warnings': [],
            'backend': 'pypdf',
        }

        state = {'count': 0}

        def side_effect(*args, **kwargs):
            state['count'] += 1
            if state['count'] == 2:
                raise RuntimeError('forced ETS persistence failure')

        persist_mock.side_effect = side_effect

        run = create_extraction_run(self.document, actor_id=self.user.pk, dry_run=False)

        run.refresh_from_db()
        self.assertEqual(run.status, SourceExtractionRun.Status.FAILED)
        self.assertIn('Pipeline failed', run.logs)
        self.assertEqual(
            ExtractedAssertionModel.objects.filter(extraction_run=run, ets_persisted=True).count(),
            0,
        )
