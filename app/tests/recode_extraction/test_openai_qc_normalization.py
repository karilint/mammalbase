from types import SimpleNamespace

from django.test import TestCase

from recode_extraction.services.qc import normalize_and_validate_trait_records


class OpenAIQcNormalizationTests(TestCase):
    def _fake_pass2(self, value):
        rec = SimpleNamespace(model_dump=lambda exclude_none=True: {
            'verbatimScientificName': 'Mus musculus',
            'taxonRank': 'species',
            'verbatimTraitName': 'head-body length',
            'verbatimTraitUnit': 'mm',
            'verbatimTraitValue': value,
            'references': 'Ref',
            'author': '0000-0000-0000-0000',
            'measurementRemarks': 'page=1',
        })
        return SimpleNamespace(traitRecords=[rec])

    def test_range_parsing(self):
        records, _ = normalize_and_validate_trait_records(self._fake_pass2('69–95'), run=SimpleNamespace(pk=1), default_reference='Ref', default_author_orcid='0000-0000-0000-0000')
        self.assertEqual(records[0]['measurementValue_min'], 69.0)
        self.assertEqual(records[0]['measurementValue_max'], 95.0)
        self.assertEqual(records[0]['statisticalMethod'], 'range')

    def test_mean_sd_parsing(self):
        records, _ = normalize_and_validate_trait_records(self._fake_pass2('20.45 ± 4.22'), run=SimpleNamespace(pk=1), default_reference='Ref', default_author_orcid='0000-0000-0000-0000')
        self.assertEqual(records[0]['measurementValue_min'], 20.45)
        self.assertEqual(records[0]['dispersion'], 4.22)
        self.assertEqual(records[0]['statisticalMethod'], 'mean ± SD')

    def test_invalid_numeric_keeps_candidate(self):
        records, summary = normalize_and_validate_trait_records(self._fake_pass2('not-a-number'), run=SimpleNamespace(pk=1), default_reference='Ref', default_author_orcid='0000-0000-0000-0000')
        self.assertEqual(len(records), 1)
        self.assertIn('records_with_errors', summary)
