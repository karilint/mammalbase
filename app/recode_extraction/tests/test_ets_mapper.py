from django.test import SimpleTestCase

from recode_extraction.mappers.ets import EtsMapper


class EtsMapperTests(SimpleTestCase):
    def test_mapper_uses_verbatim_trait(self):
        row = EtsMapper().candidate_to_ets(
            {
                'candidate_id': 9,
                'trait_text': 'body mass',
                'value_text': '5',
                'species_text': 'Homo sapiens',
                'token_ids': ['1-1'],
                'page_number': 1,
                'snippet': 'Homo sapiens body mass 5 kg',
            },
            default_reference='ref',
            default_author='auth',
            source_document_id=1,
            extraction_run_id=1,
        )
        assert row['verbatimTraitName'] == 'body mass'
        assert 'candidate_id=' in row['measurementRemarks']
