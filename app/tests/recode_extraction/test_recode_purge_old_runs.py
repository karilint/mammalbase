from datetime import timedelta
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from recode_extraction.models import SourceDocument, SourceExtractionRun


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class RecodePurgeOldRunsCommandTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='purge-user',
            email='purge@example.com',
            password='pw-123456',
        )
        self.source = SourceDocument.objects.create(
            pdf_file=SimpleUploadedFile('purge.pdf', b'%PDF-1.4\ncontent', content_type='application/pdf'),
            title='Purge Source',
            uploader=user,
        )
        self.old_run = SourceExtractionRun.objects.create(source=self.source, status=SourceExtractionRun.Status.COMPLETED)
        self.old_run.created_at = timezone.now() - timedelta(days=40)
        self.old_run.save(update_fields=['created_at'])

    def test_dry_run_does_not_delete(self):
        call_command('recode_purge_old_runs', '--days', '30', '--dry-run')
        self.assertTrue(SourceExtractionRun.objects.filter(pk=self.old_run.pk).exists())

    def test_purge_old_runs_deletes_old_rows(self):
        call_command('recode_purge_old_runs', '--days', '30')
        self.assertFalse(SourceExtractionRun.objects.filter(pk=self.old_run.pk).exists())
