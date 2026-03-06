import unittest

from recode_extraction.services.pass1_compaction import compact_pass1_evidence


class Pass1CompactionTests(unittest.TestCase):
    def test_removes_pca_and_genetic_entries(self):
        evidence = {
            'measurement_tables': [
                'PAGE 5: BW 20.4 ± 1.1; HB 80-90 mm',
                'PAGE 6: Principal component analysis table PC1 PC2 eigenvalue',
                'PAGE 9: K2P genetic distance Cyt b 0.056 ± 0.006',
            ],
            'trait_sentences': [
                'PAGE 13: head-body length of 69–95 mm.',
                'PAGE 6: Three principal components were extracted.',
            ],
            'trait_paragraphs': [
                'PAGE 2: body weight (BW), head and body length (HB), tail length (TL).',
                'PAGE 9: pairwise Kimura 2-parameter (K2P) genetic distances among taxa.',
            ],
        }
        compacted, stats = compact_pass1_evidence(evidence, max_items_per_bucket=10, max_chars_per_item=200)
        assert len(compacted['measurement_tables']) == 1
        assert len(compacted['trait_sentences']) == 1
        assert len(compacted['trait_paragraphs']) == 1
        assert stats['removed'] >= 3

    def test_caps_bucket_and_item_length(self):
        evidence = {
            'measurement_tables': ['PAGE 1: BW 20 g ' + ('x' * 300)] * 5,
            'trait_sentences': [],
            'trait_paragraphs': [],
        }
        compacted, _ = compact_pass1_evidence(evidence, max_items_per_bucket=2, max_chars_per_item=40, max_table_chars_per_item=40)
        assert len(compacted['measurement_tables']) == 2
        assert all(len(item) <= 40 for item in compacted['measurement_tables'])


if __name__ == '__main__':
    unittest.main()
