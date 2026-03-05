from django.test import SimpleTestCase

from recode_extraction.services.evaluation import relation_f1, span_f1


class EvaluationTests(SimpleTestCase):
    def test_perfect(self):
        assert span_f1([('Species', 0, 10)], [('Species', 0, 10)]) == 1.0
        assert relation_f1({('meas_Trait', 'a', 'b')}, {('meas_Trait', 'a', 'b')}) == 1.0

    def test_partial(self):
        assert span_f1([('Species', 0, 10)], [('Trait', 0, 10)]) < 1.0
        assert relation_f1({('meas_Trait', 'a', 'b')}, {('meas_Species', 'a', 'b')}) < 1.0
