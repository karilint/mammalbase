from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from exports.models import ExportFile
from middleware.current_user import _user

User = get_user_model()

class ExportFileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        _user.value = self.user

        self.test_file = SimpleUploadedFile(
            'exports/test_export.zip',
            b'export-data',
            content_type='application/zip'
        )

    def test_export_file_creation(self):
        export = ExportFile.objects.create(file=self.test_file)
        self.assertIsNotNone(export.pk)
        self.assertTrue(export.file.name.endswith('test_export.zip'))

    def test_export_string_representation(self):
        export = ExportFile.objects.create(file=self.test_file)
        self.assertEqual(str(export), export.file.name)
