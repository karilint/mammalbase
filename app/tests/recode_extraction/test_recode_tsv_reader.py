from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from recode_extraction.adapters import RecodeTsvReader


FIXTURE_ROOT = Path(__file__).resolve().parent / 'assets' / 'recode_fixture'


class RecodeTsvReaderTests(SimpleTestCase):
    def test_reader_loads_entities_relations_and_provenance(self):
        reader = RecodeTsvReader(FIXTURE_ROOT / 'index.json')

        documents = reader.load_documents()

        self.assertEqual(len(documents), 2)

        doc100 = next(doc for doc in documents if doc.doc_id == 'DOC100')
        self.assertEqual(doc100.annotator, None)
        self.assertEqual(doc100.taxon_group, 'araneae')
        self.assertEqual(len(doc100.entities), 3)
        self.assertEqual(doc100.entities[0].entity_type, 'TAXON')
        self.assertEqual(doc100.entities[0].text, 'Canis lupus')

        doc200 = next(doc for doc in documents if doc.doc_id == 'DOC200')
        self.assertEqual(doc200.annotator, 'annotator_anna')
        self.assertEqual(len(doc200.relations), 1)
        relation = doc200.relations[0]
        self.assertEqual(relation.relation_type, 'has_trait')
        self.assertEqual(relation.head_entity_id, 'E1')
        self.assertEqual(relation.tail_entity_id, 'E2')

    def test_reader_uses_index_cache(self):
        RecodeTsvReader._documents_cache.clear()
        reader = RecodeTsvReader(FIXTURE_ROOT / 'index.json')

        with mock.patch.object(reader, '_parse_tsv', wraps=reader._parse_tsv) as parse_mock:
            reader.load_documents()
            reader.load_documents()

        self.assertEqual(parse_mock.call_count, 2)
