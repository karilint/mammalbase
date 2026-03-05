from pathlib import Path
from django.test import SimpleTestCase

from recode_extraction.adapters.webanno_parser import parse_webanno_tsv33

FIX = Path(__file__).parent / 'fixtures' / 'webanno_tsv33'


class WebAnnoParserTests(SimpleTestCase):
    def test_simple(self):
        parsed_doc = parse_webanno_tsv33(str(FIX / 'simple_trait_measurement.tsv'))
        assert len(parsed_doc.tokens) > 0
        assert any(s.label == 'Species' and s.disambig == 1 for s in parsed_doc.spans)
        assert any(s.label == 'TraitVal' for s in parsed_doc.spans)
        assert any(r.label in {'meas_Trait', 'meas_Species', 'meas_Unit'} for r in parsed_doc.relations)

    def test_stacked(self):
        parsed_doc = parse_webanno_tsv33(str(FIX / 'stacked_annotations.tsv'))
        assert len({s.label for s in parsed_doc.spans}) > 3
        assert len(parsed_doc.relations) > 1

    def test_disambiguation(self):
        parsed_doc = parse_webanno_tsv33(str(FIX / 'disambiguation_relation.tsv'))
        assert any(s.label == 'Species' and s.disambig == 1 for s in parsed_doc.spans)
        assert any(r.endpoint_disambig == (1, 2) for r in parsed_doc.relations)
