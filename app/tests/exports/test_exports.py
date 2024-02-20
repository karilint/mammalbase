import os

from django.test import TestCase
from django.db import models, connection

from mb.models.models import EntityClass, MasterEntity
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
            'email_recipient': self.email,
            'export_list': [
                {
                    'file_name': self.file_name,
                    'queries_and_fields': [(
                        self.query,
                        list(zip(self.fields, self.headers))
                    )],
                }
            ],
            'export_file_id': export_file_id
        }

    def test_export_zip_file_fails_on_empty_email(self):
        self.export_args['email_recipient'] = ''
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
        self.export_args['export_list'] = []
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

    def test_export_zip_file_fails_on_empty_queries_and_fields(self):
        self.export_args['export_list'][0]['queries_and_fields'] = []
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

    def test_export_zip_file_fails_on_query_with_no_fields(self):
        self.export_args['export_list'][0]['queries_and_fields'] = [
            (self.query,[])
        ]
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

    def test_export_zip_file_fails_on_mismatched_fields(self):
        self.export_args['export_list'][0]['queries_and_fields'] = [
            (self.query,[self.fields]),
            (self.query,[('f1', 'F1'), ('f2', 'F2'),('f3', 'F3')])
        ]
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
        self.export_args['export_list'][0]['file_name'] = ''
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
        class ExportTestClass(models.Model):
            animal = models.CharField(max_length=255)
            afraid = models.CharField(max_length=255)
            age = models.IntegerField()
            class Meta:
                managed = False
                db_table = "test_export_zip_file"
                app_label = "test"
        connection.schema_editor().create_model(ExportTestClass)
        data = [
            ('Norsu', 'Hiiri', 12),
            ('Mirri', 'Vesi', None),
            ('Sifaka', '', 3),
        ]
        excepted_output = [
            'Name\tAfraid\tAge\n',
            'Norsu\tHiiri\t12\n',
            'Mirri\tVesi\tNA\n',
            'Sifaka\tNA\t0\n',
        ]
        for animal, afraid, age in data:
            ExportTestClass(animal=animal, afraid=afraid, age=age).save()
        export_zip_file(
            email_recipient='testi@testi.fi',
            export_list=[
                {
                    'file_name': 'entity_class',
                    'queries_and_fields': [(
                        ExportTestClass.objects.all(),
                        [
                            ('animal', 'Name'),
                            ('afraid', 'Afraid'),
                            ('age', 'Age')
                        ]
                    )]
                }
            ],
            export_file_id=123,
            file_writer=self.test_writer
        )
        for row, expected_row in zip(
                self.test_writer.files[0][1],
                excepted_output):
            self.assertEqual(row, expected_row)
