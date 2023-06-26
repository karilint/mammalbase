import os

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from mb.models import EntityClass, MasterEntity
from exports.tasks import export_zip_file
from exports.models import ExportFile
from .utils.test_export_file_writer import TestExportFileWriter

class ExportZipFileTestCase(TestCase):
    def setUp(self):
        self.current_dir = os.getcwd()
        self.test_writer = TestExportFileWriter()

        export_file = ExportFile(file=None)
        export_file.save()
        export_file_id = export_file.pk
        self.email = 'test@email.com'
        self.query = MasterEntity.objects.all()
        self.file_name = 'master_entity_all'
        self.fields = [
            'name',
            'entity__name',
            'taxon__scientific_name',
        ]
        self.headers = [
            'Name',
            'Entity',
            'Scientific name',
        ]
        self.export_args = {
            'email_receiver': self.email,
            'queries': [{
                'file_name': self.file_name,
                'fields': list(zip(self.fields, self.headers)),
                'query_set': self.query
            }],
            'export_file_id': export_file_id
        }

    def test_export_zip_file_fails_on_empty_email(self):
        self.export_args['email_receiver'] = ''
        self.assertRaises(
            ValueError,
            export_zip_file,
            **self.export_args,
            file_writer=self.test_writer,
        )
        self.assertEqual(
            self.current_dir,
            os.getcwd()
        )

    def test_export_zip_file_fails_on_empty_query_list(self):
        self.export_args['queries'] = []
        self.assertRaises(
            ValueError,
            export_zip_file,
            **self.export_args,
            file_writer=self.test_writer,
        )
        self.assertEqual(
            self.current_dir,
            os.getcwd()
        )

    def test_export_zip_file_fails_on_empty_fields_list(self):
        self.export_args['queries'][0]['fields'] = []
        self.assertRaises(
            ValueError,
            export_zip_file,
            **self.export_args,
            file_writer=self.test_writer,
        )
        self.assertEqual(
            self.current_dir,
            os.getcwd()
        )

    def test_export_zip_file_fails_on_empty_file_name(self):
        self.export_args['queries'][0]['file_name'] = ''
        self.assertRaises(
            ValueError,
            export_zip_file,
            **self.export_args,
            file_writer=self.test_writer,
        )
        self.assertEqual(
            self.current_dir,
            os.getcwd()
        )


    def test_export_zip_file_writes_correct_lines(self):
        animals = ['Norsu', 'Mirri', 'Sifaka']
        for animal in animals:
            EntityClass(name=animal).save()
        export_zip_file(
            email_receiver='testi@testi.fi',
            queries=[{
                'file_name': 'entity_class',
                'fields': [('name', 'Name')],
                'query_set': EntityClass.objects.all()
            }],
            export_file_id=123,
            file_writer=self.test_writer
        )
        first_column_items = []
        for row in self.test_writer.files[0][1]:
            first_column_items.append(row[0])
        self.assertIn('Name', first_column_items)
        self.assertTrue(all(x in first_column_items for x in animals))
