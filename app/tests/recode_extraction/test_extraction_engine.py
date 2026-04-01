from django.test import SimpleTestCase

from recode_extraction.services import ExtractionEngine


class ExtractionEngineTests(SimpleTestCase):
    def test_baseline_extractor_returns_normalized_assertions(self):
        text = (
            'Canis lupus body mass is 12 kg. '
            'Adult mass was 11 kg. '
            'Litter size is 4. '
            'Dietary class is carnivore.'
        )

        engine = ExtractionEngine()
        assertions = engine.extract(text)

        self.assertGreaterEqual(len(assertions), 4)
        self.assertTrue(any(item.trait_name == 'body mass' and item.value == '12' for item in assertions))
        self.assertTrue(any(item.trait_name == 'adult mass' and item.unit == 'kg' for item in assertions))
        self.assertTrue(any(item.trait_name == 'litter size' and item.value == '4' for item in assertions))
        self.assertTrue(any(item.trait_name == 'dietary class' for item in assertions))

        first = assertions[0]
        self.assertGreaterEqual(first.confidence, 0)
        self.assertLessEqual(first.confidence, 1)
        self.assertTrue(first.evidence_spans)
