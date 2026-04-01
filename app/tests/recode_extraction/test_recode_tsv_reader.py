from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from recode_extraction.adapters import RecodeTsvReader


FIXTURE_ROOT = Path(__file__).resolve().parent / 'assets' / 'recode_fixture'


class RecodeTsvReaderTests(SimpleTestCase):
    def test_reader_loads_webanno_entities_relations_and_provenance(self):
        reader = RecodeTsvReader(FIXTURE_ROOT / 'index.json')

        documents = reader.load_documents()

        self.assertEqual(len(documents), 2)

        doc100 = next(doc for doc in documents if doc.doc_id == 'DOC100')
        self.assertIsNone(doc100.annotator)
        self.assertEqual(doc100.taxon_group, 'araneae')
        self.assertTrue(any(item.entity_type == 'Species' and 'Canis lupus' in item.text for item in doc100.entities))
        self.assertTrue(any(item.entity_type == 'TraitVal' and item.text == '12' for item in doc100.entities))
        self.assertTrue(any(rel.relation_type == 'meas_trait' for rel in doc100.relations))

        doc200 = next(doc for doc in documents if doc.doc_id == 'DOC200')
        self.assertEqual(doc200.annotator, 'annotator_anna')
        self.assertTrue(any(item.entity_type == 'Unit' and item.text == 'cm' for item in doc200.entities))
        self.assertTrue(any(rel.relation_type == 'meas_unit' for rel in doc200.relations))

    def test_reader_uses_index_cache(self):
        RecodeTsvReader._documents_cache.clear()
        reader = RecodeTsvReader(FIXTURE_ROOT / 'index.json')

        with mock.patch.object(reader, '_parse_tsv', wraps=reader._parse_tsv) as parse_mock:
            reader.load_documents()
            reader.load_documents()

        self.assertEqual(parse_mock.call_count, 2)
