from django.test import TestCase
from exports.tasks import enter_temp_dir, exit_temp_dir
from exports.models import ExportFile
from exports.utilities.export_file_writer import ExportFileWriter

class ExportFileWriterTestCase(TestCase):
    def setUp(self):
        self.current_dir, self.temp_dir = enter_temp_dir()
        self.writer = ExportFileWriter()

    def tearDown(self):
        exit_temp_dir(self.current_dir, self.temp_dir)

    def test_export_file_writer_saves_zip_to_db(self):
        file = open(self.writer.zip_file_path, 'w')
        file.close()
        export_file = ExportFile(file=None)
        export_file.save()
        export_file_id = export_file.pk
        self.writer.save_zip_to_django_model(export_file_id)
        export_file = ExportFile.objects.get(id=export_file_id)
        self.assertIsNotNone(export_file.file)
