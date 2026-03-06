from django.test import SimpleTestCase

from recode_extraction.services.table_measurement_parser import extract_trait_records_from_measurement_tables


class TableMeasurementParserTests(SimpleTestCase):
    def test_extracts_skull_and_external_rows(self):
        table = (
            "PAGE 5: Table 1 ... M. p. pahari (N = 33) M. p. jacksoniae (N = 22) M. p. gairdneri (N = 5) "
            "BW 20.45 ± 4.22 23.55 ± 4.87 19.10 ± 7.17 13.4–28.0(33) 15.4–32(22) 13–30.8(5) "
            "GLS 23.42 ± 0.89 22.20 ± 1.16 21.48 ± 0.10 21.14–24.77(20) 20.31–24.69(16) 21.48–21.48(1)"
        )
        records = extract_trait_records_from_measurement_tables([table], abbr_dict={})

        names = {(r['verbatimScientificName'], r['verbatimTraitName']) for r in records}
        self.assertIn(('Mus pahari pahari', 'Body Mass'), names)
        self.assertIn(('Mus pahari jacksoniae', 'Body Mass'), names)
        self.assertIn(('Mus pahari gairdneri', 'Greatest Length of Skull'), names)

    def test_dedupes_records(self):
        table = (
            "M. p. pahari (N = 33) M. p. jacksoniae (N = 22) M. p. gairdneri (N = 5) "
            "BW 20.45 ± 4.22 23.55 ± 4.87 19.10 ± 7.17 13.4–28.0(33) 15.4–32(22) 13–30.8(5) "
            "BW 20.45 ± 4.22 23.55 ± 4.87 19.10 ± 7.17 13.4–28.0(33) 15.4–32(22) 13–30.8(5)"
        )
        records = extract_trait_records_from_measurement_tables([table], abbr_dict={})
        uniq = {(r['verbatimScientificName'], r['verbatimTraitName'], r['statisticalMethod'], r['verbatimTraitValue']) for r in records}
        self.assertEqual(len(records), len(uniq))

    def test_handles_single_mean_without_sd(self):
        table = (
            "M. p. pahari (N = 33) M. p. jacksoniae (N = 22) M. p. gairdneri (N = 5) "
            "GLS 23.42 ± 0.89 22.20 ± 1.16 21.48 21.14–24.77(20) 20.31–24.69(16) 21.48–21.48(1)"
        )
        records = extract_trait_records_from_measurement_tables([table], abbr_dict={})
        mean_records = [
            r for r in records
            if r['verbatimScientificName'] == 'Mus pahari gairdneri'
            and r['verbatimTraitName'] == 'Greatest Length of Skull'
            and r['statisticalMethod'] in {'mean', 'mean ± SD'}
        ]
        self.assertTrue(mean_records)
        self.assertEqual(mean_records[0]['verbatimTraitValue'], '21.48')
