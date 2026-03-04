import tempfile
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from recode_extraction.models import SourceDocument, SourceExtractionRun
from recode_extraction.services.orchestrator import RecodePipelineRunner


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class RecodePipelineRunnerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='runner-user',
            email='runner@example.com',
            password='pw-123456',
        )
        self.document = SourceDocument.objects.create(
            pdf_file=SimpleUploadedFile('runner.pdf', b'%PDF-1.4\ncontent', content_type='application/pdf'),
            title='Runner Source',
            year=2024,
            uploader=self.user,
        )

    @mock.patch('recode_extraction.services.orchestrator.PdfToTextService.extract')
    def test_runner_completes_and_updates_progress(self, extract_mock):
        extract_mock.return_value = {
            'pages': [{'page_number': 1, 'text': 'Canis lupus body mass is 12 kg.'}],
            'full_text': 'Canis lupus body mass is 12 kg.',
            'extraction_warnings': [],
            'backend': 'pypdf',
        }

        run = RecodePipelineRunner().run(
            self.document.pk,
            run_params={
                'actor_id': self.user.pk,
                'dry_run': True,
                'extraction_backend': 'baseline',
                'confidence_threshold': 0.0,
                'mapping_version': 'v1',
            },
        )

        run.refresh_from_db()
        self.assertEqual(run.status, SourceExtractionRun.Status.COMPLETED)
        self.assertEqual(run.current_stage, 'completed')
        self.assertEqual(run.progress_percent, 100)
        self.assertEqual(run.parameters['extraction_backend'], 'baseline')
