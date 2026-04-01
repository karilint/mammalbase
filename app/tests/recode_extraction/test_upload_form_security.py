from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings

from recode_extraction.forms import SourceDocumentUploadForm


class SourceDocumentUploadFormSecurityTests(SimpleTestCase):
    @override_settings(RECODE_MAX_PDF_MB=1)
    def test_rejects_non_pdf_magic_bytes(self):
        form = SourceDocumentUploadForm(
            data={'title': 'Bad file'},
            files={'pdf_file': SimpleUploadedFile('bad.pdf', b'NOTPDF', content_type='application/pdf')},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('missing %PDF- signature', form.errors['pdf_file'][0])

    @override_settings(RECODE_MAX_PDF_MB=1)
    def test_rejects_oversized_pdf(self):
        payload = b'%PDF-' + b'a' * (2 * 1024 * 1024)
        form = SourceDocumentUploadForm(
            data={'title': 'Big file'},
            files={'pdf_file': SimpleUploadedFile('big.pdf', payload, content_type='application/pdf')},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('maximum allowed size', form.errors['pdf_file'][0])

    @override_settings(RECODE_MAX_PDF_MB=5)
    def test_sanitizes_path_like_filename(self):
        form = SourceDocumentUploadForm(
            data={'title': 'Traversal'},
            files={'pdf_file': SimpleUploadedFile('../evil.pdf', b'%PDF-1.4\ncontent', content_type='application/pdf')},
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['pdf_file'].name, 'evil.pdf')
