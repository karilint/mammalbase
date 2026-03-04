import tempfile
from pathlib import Path
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from recode_extraction.models import SourceDocument, SourceExtractionRun
from recode_extraction.services.pdf_text import PdfToTextService
from recode_extraction.services.runs import create_extraction_run


ASSETS_DIR = Path(__file__).resolve().parent / 'assets'


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PdfToTextServiceTests(TestCase):
    def test_extract_preserves_page_boundaries(self):
        service = PdfToTextService()
        package = service.extract(ASSETS_DIR / 'normal_text.pdf')

        self.assertEqual(package['backend'], 'pypdf')
        self.assertEqual(len(package['pages']), 2)
        self.assertEqual(package['pages'][0]['page_number'], 1)
        self.assertIn('First page text', package['pages'][0]['text'])
        self.assertIn('Second page text', package['pages'][1]['text'])
        self.assertIn('First page text', package['full_text'])
        self.assertIn('Second page text', package['full_text'])

    def test_extract_adds_warning_for_empty_page_text(self):
        service = PdfToTextService()
        package = service.extract(ASSETS_DIR / 'broken_encoding.pdf')

        self.assertEqual(len(package['pages']), 2)
        self.assertTrue(any('No text extracted on page 2' in item for item in package['extraction_warnings']))

    def test_run_persists_extracted_text_package(self):
        user = get_user_model().objects.create_user(
            username='pdf-user',
            email='pdf-user@example.com',
            password='test-password-123',
        )

        pdf_bytes = (ASSETS_DIR / 'single_page.pdf').read_bytes()
        source = SourceDocument.objects.create(
            pdf_file=SimpleUploadedFile('single_page.pdf', pdf_bytes, content_type='application/pdf'),
            title='Single page source',
            uploader=user,
        )

        run = create_extraction_run(source, actor_id=user.pk)

        run.refresh_from_db()
        self.assertEqual(run.status, SourceExtractionRun.Status.COMPLETED)
        self.assertIn('pages', run.extracted_text_package)
        self.assertEqual(run.extracted_text_package['pages'][0]['page_number'], 1)
        self.assertIn('Lone page', run.extracted_text_package['full_text'])

    @override_settings(RECODE_TIMEOUT_SECONDS=30)
    def test_extract_uses_cache_on_repeated_calls(self):
        service = PdfToTextService()
        with mock.patch.object(service, '_extract_with_pypdf') as extract_mock:
            extract_mock.return_value = mock.Mock(to_dict=lambda: {
                'pages': [{'page_number': 1, 'text': 'cached'}],
                'full_text': 'cached',
                'extraction_warnings': [],
                'backend': 'pypdf',
            })

            first = service.extract(ASSETS_DIR / 'single_page.pdf')
            second = service.extract(ASSETS_DIR / 'single_page.pdf')

        self.assertEqual(first, second)
        extract_mock.assert_called_once()
