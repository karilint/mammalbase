from django.test import TestCase
from app.imports.importers.base_importer import BaseImporter

class BaseImporterTest(TestCase):
    def setUp(self):
        self.base_importer = BaseImporter()