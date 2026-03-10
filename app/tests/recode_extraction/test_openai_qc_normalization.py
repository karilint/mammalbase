from types import SimpleNamespace

from django.test import TestCase

from recode_extraction.services.qc import normalize_and_validate_trait_records


class OpenAIQcNormalizationTests(TestCase):
    def _fake_pass2(self, value, *, scientific_name='Mus musculus', references='Doe, 2024. Example Title.'):
        rec = SimpleNamespace(model_dump=lambda exclude_none=True: {
            'verbatimScientificName': scientific_name,
            'taxonRank': 'species',
            'verbatimTraitName': 'head-body length',
            'verbatimTraitUnit': 'mm',
            'verbatimTraitValue': value,
            'references': references,
            'author': '0000-0000-0000-0000',
            'measurementRemarks': 'page=1',
        })
        return SimpleNamespace(traitRecords=[rec])

    def _run(self, pass2):
        return normalize_and_validate_trait_records(
            pass2,
            run=SimpleNamespace(pk=1, extracted_text_package={'full_text': 'Mus pahari pahari and Mus jacksoniae were measured.'}),
            default_reference='Author, 2024. Canonical Paper.',
            default_author_orcid='0000-0000-0000-0000',
        )

    def test_range_parsing(self):
        records, _ = self._run(self._fake_pass2('69–95'))
        self.assertEqual(records[0]['measurementValue_min'], 69.0)
        self.assertEqual(records[0]['measurementValue_max'], 95.0)
        self.assertEqual(records[0]['statisticalMethod'], 'range')

    def test_mean_sd_parsing(self):
        records, _ = self._run(self._fake_pass2('20.45 ± 4.22'))
        self.assertEqual(records[0]['measurementValue_min'], 20.45)
        self.assertEqual(records[0]['dispersion'], 4.22)
        self.assertEqual(records[0]['statisticalMethod'], 'mean ± SD')

    def test_invalid_numeric_keeps_candidate(self):
        records, summary = self._run(self._fake_pass2('not-a-number'))
        self.assertEqual(len(records), 1)
        self.assertIn('records_with_errors', summary)

    def test_reference_falls_back_to_canonical_when_invalid(self):
        records, _ = self._run(self._fake_pass2('12', references='PAGE 5: Table 1'))
        self.assertEqual(records[0]['references'], 'Author, 2024. Canonical Paper.')

    def test_scientific_name_expands_from_document_text(self):
        records, _ = self._run(self._fake_pass2('12', scientific_name='M. p. pahari'))
        self.assertEqual(records[0]['verbatimScientificName'], 'Mus pahari pahari')


    def test_associated_references_blank_when_non_citable_text(self):
        rec = SimpleNamespace(model_dump=lambda exclude_none=True: {
            'verbatimScientificName': 'Mus musculus',
            'taxonRank': 'species',
            'verbatimTraitName': 'head-body length',
            'verbatimTraitUnit': 'mm',
            'verbatimTraitValue': '12',
            'references': 'Doe, 2024. Example Title.',
            'associatedReferences': 'Table note only',
            'measurementRemarks': 'page=1',
        })
        records, _ = self._run(SimpleNamespace(traitRecords=[rec]))
        self.assertEqual(records[0]['associatedReferences'], '')

    def test_associated_references_keeps_original_study_or_year(self):
        rec1 = SimpleNamespace(model_dump=lambda exclude_none=True: {
            'verbatimScientificName': 'Mus musculus',
            'taxonRank': 'species',
            'verbatimTraitName': 'head-body length',
            'verbatimTraitUnit': 'mm',
            'verbatimTraitValue': '12',
            'references': 'Doe, 2024. Example Title.',
            'associatedReferences': 'Original study',
            'measurementRemarks': 'page=1',
        })
        rec2 = SimpleNamespace(model_dump=lambda exclude_none=True: {
            'verbatimScientificName': 'Mus musculus',
            'taxonRank': 'species',
            'verbatimTraitName': 'tail length',
            'verbatimTraitUnit': 'mm',
            'verbatimTraitValue': '20',
            'references': 'Doe, 2024. Example Title.',
            'associatedReferences': 'Smith et al., 2025',
            'measurementRemarks': 'page=1',
        })
        records, _ = self._run(SimpleNamespace(traitRecords=[rec1, rec2]))
        self.assertEqual(records[0]['associatedReferences'], 'Original study')
        self.assertEqual(records[1]['associatedReferences'], 'Smith et al., 2025')


    def test_references_always_use_default_source_citation(self):
        rec = SimpleNamespace(model_dump=lambda exclude_none=True: {
            'verbatimScientificName': 'Mus musculus',
            'taxonRank': 'species',
            'verbatimTraitName': 'head-body length',
            'verbatimTraitUnit': 'mm',
            'verbatimTraitValue': '12',
            'references': 'Smith et al., 2025. Different paper.',
            'measurementRemarks': 'page=1',
        })
        records, _ = self._run(SimpleNamespace(traitRecords=[rec]))
        self.assertEqual(records[0]['references'], 'Author, 2024. Canonical Paper.')
