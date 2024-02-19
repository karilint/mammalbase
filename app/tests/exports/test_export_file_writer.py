from django.test import TestCase
from exports.tasks import enter_temp_dir, exit_temp_dir
from exports.models import ExportFile
from exports.utilities.export_file_writer import ExportFileWriter
from zipfile import ZipFile

""" TODO: Remake export unit tests
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

    def test_export_file_writer_zip(self):
        file1 = open('file1', 'w')
        file1.close()
        file2 = open('file2', 'w')
        file2.close()
        files = ['file1', 'file2']
        self.writer.zip(files)
        zip_file = ZipFile(self.writer.zip_file_path)
        self.assertIn('file1', zip_file.namelist())
        self.assertIn('file2', zip_file.namelist())

    def test_export_file_writer_write_rows(self):
        file_path = 'file_name'
        headers = ['header1', 'header2']
        rows = [['1', '2'], ['3', '4']]
        self.writer.write_rows(file_path, headers, rows)
        file = open(file_path, 'r')
        file_contents = file.readlines()
        self.assertEqual(file_contents[0], 'header1\theader2\n')
        self.assertEqual(file_contents[1], '1\t2\n')
        self.assertEqual(file_contents[2], '3\t4\n')
"""