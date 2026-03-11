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

    def _pass2_with_metadata(self, records, citation='Meta, 2024. Meta Citation.', author='1111-2222-3333-4444'):
        return SimpleNamespace(traitRecords=records, metadata=SimpleNamespace(citation=citation, author=author))

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

    def test_scientific_name_ocr_hyphen_is_removed(self):
        records, _ = self._run(self._fake_pass2('12', scientific_name='Mus pahari gaird-neri'))
        self.assertEqual(records[0]['verbatimScientificName'], 'Mus pahari gairdneri')
        self.assertEqual(records[0]['taxonRank'], 'subspecies')

    def test_metadata_citation_and_author_are_used(self):
        rec = SimpleNamespace(model_dump=lambda exclude_none=True: {
            'verbatimScientificName': 'Mus musculus',
            'taxonRank': 'species',
            'verbatimTraitName': 'head-body length',
            'verbatimTraitUnit': 'mm',
            'verbatimTraitValue': '12',
            'measurementRemarks': 'page=1',
        })
        records, _ = self._run(self._pass2_with_metadata([rec]))
        self.assertEqual(records[0]['references'], 'Meta, 2024. Meta Citation.')
        self.assertEqual(records[0]['author'], '1111-2222-3333-4444')


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


    def test_orig_abbr_moved_to_trait_name(self):
        rec = SimpleNamespace(model_dump=lambda exclude_none=True: {
            'verbatimScientificName': 'Mus musculus',
            'taxonRank': 'species',
            'verbatimTraitName': 'Body Weight',
            'verbatimTraitUnit': 'g',
            'verbatimTraitValue': '20.45',
            'measurementValue_min': 13.4,
            'measurementValue_max': 28.0,
            'dispersion': 4.22,
            'statisticalMethod': 'mean ± SD, range',
            'references': 'Doe, 2024. Example Title.',
            'measurementRemarks': 'orig_abbr=BW page=1',
        })
        records, _ = self._run(SimpleNamespace(traitRecords=[rec]))
        self.assertEqual(records[0]['verbatimTraitName'], 'Body Weight (BW)')
        self.assertNotIn('orig_abbr=', records[0]['measurementRemarks'])

    def test_mean_and_range_stay_on_same_row(self):
        rec = SimpleNamespace(model_dump=lambda exclude_none=True: {
            'verbatimScientificName': 'Mus musculus',
            'taxonRank': 'species',
            'verbatimTraitName': 'Body Weight (BW)',
            'verbatimTraitUnit': 'g',
            'verbatimTraitValue': '20.45 ± 4.22',
            'measurementValue_min': 13.4,
            'measurementValue_max': 28.0,
            'statisticalMethod': 'range',
            'references': 'Doe, 2024. Example Title.',
            'measurementRemarks': 'page=1',
        })
        records, _ = self._run(SimpleNamespace(traitRecords=[rec]))
        self.assertEqual(records[0]['measurementValue_min'], 13.4)
        self.assertEqual(records[0]['measurementValue_max'], 28.0)
        self.assertEqual(records[0]['verbatimTraitValue'], '20.45')
        self.assertIn('mean ± SD', records[0]['statisticalMethod'])
        self.assertIn('range', records[0]['statisticalMethod'])
