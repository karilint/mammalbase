import os
import tempfile
from unittest import mock
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from recode_extraction.models import SourceDocument, SourceExtractionRun


ASSETS_DIR = Path(__file__).resolve().parent / 'assets'


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class SourceDocumentViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='recode-user',
            email='recode@example.com',
            password='test-password-123',
        )
        self.client.force_login(self.user)

    def test_upload_pdf_creates_document_and_stores_file(self):
        payload = {
            'title': 'Test Source',
            'authors': 'Jane Doe',
            'year': 2024,
            'doi': '10.1000/test',
            'pdf_file': SimpleUploadedFile('source.pdf', b'%PDF-1.4\ncontent', content_type='application/pdf'),
        }

        response = self.client.post(reverse('recode_source_document_upload'), data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(SourceDocument.objects.count(), 1)
        document = SourceDocument.objects.get()
        self.assertTrue(document.pdf_file.name.endswith('.pdf'))
        self.assertEqual(document.uploader, self.user)

    def test_run_extraction_creates_queued_run(self):
        document = SourceDocument.objects.create(
            pdf_file=SimpleUploadedFile('existing.pdf', (ASSETS_DIR / 'single_page.pdf').read_bytes(), content_type='application/pdf'),
            title='Existing Source',
            uploader=self.user,
        )

        response = self.client.post(reverse('recode_source_document_run', kwargs={'pk': document.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(SourceExtractionRun.objects.count(), 1)
        run = SourceExtractionRun.objects.get()
        self.assertEqual(run.source, document)
        self.assertEqual(run.status, SourceExtractionRun.Status.COMPLETED)
        self.assertIn('pages', run.extracted_text_package)

    @mock.patch('recode_extraction.views.run_recode_pipeline.delay')
    def test_run_extraction_async_queues_background_task(self, delay_mock):
        os.environ['RECODE_ASYNC'] = '1'
        try:
            document = SourceDocument.objects.create(
                pdf_file=SimpleUploadedFile('existing.pdf', (ASSETS_DIR / 'single_page.pdf').read_bytes(), content_type='application/pdf'),
                title='Async Source',
                uploader=self.user,
            )
            response = self.client.post(reverse('recode_source_document_run', kwargs={'pk': document.pk}), data={
                'extraction_backend': 'baseline',
                'confidence_threshold': '0.2',
            })
            self.assertEqual(response.status_code, 302)
            delay_mock.assert_called_once()
        finally:
            os.environ.pop('RECODE_ASYNC', None)
