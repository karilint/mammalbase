from django.test import TestCase

import mb.models
from exports.tasks import export_zip_file
from exports.models import ExportFile
from django.core.exceptions import ObjectDoesNotExist


class ExportZipFileTestCase(TestCase):
    def setUp(self):
        export_file = ExportFile(file=None)
        export_file.save()
        export_file_id = export_file.pk
        self.email = 'test@email.com'
        self.query = mb.models.MasterEntity.objects.all()
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
            **self.export_args
        )

    def test_export_zip_file_fails_on_empty_query_list(self):
        self.export_args['queries'] = []
        self.assertRaises(
            ValueError,
            export_zip_file,
            **self.export_args
        )

    def test_export_zip_file_fails_on_empty_fields_list(self):
        self.export_args['queries'][0]['fields'] = []
        self.assertRaises(
            ValueError,
            export_zip_file,
            **self.export_args
        )

    def test_export_zip_file_fails_on_empty_file_name(self):
        self.export_args['queries'][0]['file_name'] = ''
        self.assertRaises(
            ValueError,
            export_zip_file,
            **self.export_args
        )

    def test_export_zip_file_fails_on_invalid_export_file_id(self):
        self.export_args['export_file_id'] = 123
        self.assertRaises(
            ObjectDoesNotExist,
            export_zip_file,
            **self.export_args
        )