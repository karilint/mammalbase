from pathlib import Path
from django.test import TestCase

from recode_extraction.adapters.webanno_parser import parse_webanno_tsv33
from recode_extraction.models import SourceDocument, SourceExtractionRun
from recode_extraction.services.candidate_builder import build_graph, build_measurement_candidates
from recode_extraction.services.persistence import persist_parsed_doc

FIX = Path(__file__).parent / 'fixtures' / 'webanno_tsv33'


class CandidateBuilderTests(TestCase):
    def _run_for(self, fixture):
        doc = SourceDocument.objects.create(pdf_file='x.pdf', title='t')
        run = SourceExtractionRun.objects.create(source=doc)
        parsed = parse_webanno_tsv33(str(FIX / fixture))
        persist_parsed_doc(run, parsed, page_number=1, snippet_source_text='snippet')
        g = build_graph(run)
        return build_measurement_candidates(g, relation_config={})

    def test_simple_candidate(self):
        candidates = self._run_for('simple_trait_measurement.tsv')
        assert len(candidates) == 1
        assert candidates[0]['trait_text'] == 'body mass'
        assert candidates[0]['species_text'].startswith('Homo')

    def test_stacked(self):
        candidates = self._run_for('stacked_annotations.tsv')
        assert len(candidates) >= 1

    def test_disambig(self):
        candidates = self._run_for('disambiguation_relation.tsv')
        assert len(candidates) >= 1
