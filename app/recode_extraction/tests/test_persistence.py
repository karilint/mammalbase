from pathlib import Path
from django.test import TestCase

from recode_extraction.adapters.webanno_parser import parse_webanno_tsv33
from recode_extraction.models import ExtractedEntity, ExtractedRelation, SourceDocument, SourceExtractionRun
from recode_extraction.services.persistence import persist_parsed_doc


class PersistenceTests(TestCase):
    def test_idempotent(self):
        doc = SourceDocument.objects.create(pdf_file='x.pdf', title='t')
        run = SourceExtractionRun.objects.create(source=doc)
        parsed = parse_webanno_tsv33(str(Path(__file__).parent / 'fixtures/webanno_tsv33/simple_trait_measurement.tsv'))
        persist_parsed_doc(run, parsed, page_number=1, snippet_source_text='abc')
        first = (ExtractedEntity.objects.count(), ExtractedRelation.objects.count())
        persist_parsed_doc(run, parsed, page_number=1, snippet_source_text='abc')
        second = (ExtractedEntity.objects.count(), ExtractedRelation.objects.count())
        assert first == second
