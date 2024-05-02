import unittest
from django.test import TestCase
from itis.tools import calculate_data_quality_score

class TestCalculateDataQualityScore(TestCase):

    def test_data_quality_score(self):
        score = calculate_data_quality_score('Species', 'some study', 'book', None, 0, 0, 0, 0, None, '')
    
        self.assertEqual(score, 4)

        score2 = calculate_data_quality_score('Species', 'Original study', 'journal-article', 'big', 2, 2, 2, 2, 'Big method', '')

        self.assertEqual(score2, 12)