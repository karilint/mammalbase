from django.test import TestCase
import pandas as pd


class ValidationTest(TestCase):
    def test_check_headers_ds(self):
        self.assertEqual(self.check.check_headers_ds(self.file), True)
    
    def test_check_headers_ets(self):
        self.assertEqual(self.check.check_headers_ets(self.file_ets), True)

    def test_check_headers_pa(self):
        self.assertEqual(self.check.check_headers_pa(self.file_pa), True)

    def test_check_headers_ds_false(self):
        self.assertEqual(self.check.check_headers_ds(self.false_file), False)
    
    def test_check_headers_ets_false(self):
        self.assertEqual(self.check.check_headers_ets(self.file), False)

    def test_check_headers_pa_false(self):
        self.assertEqual(self.check.check_headers_pa(self.file_pa_invalid_headers), False)

    def test_check_author(self):
        self.assertEqual(self.check.check_author(self.file), True)
    
    def test_check_verbatimScientificName(self):
        self.assertEqual(self.check.check_verbatimScientificName(self.file), True)
    
    def test_false_check_verbatimScientificName_four_words(self):
        self.assertEqual(self.check.check_verbatimScientificName(self.false_file), False)

    def test_false_check_verbatimScientificName_three_words(self):
        self.assertEqual(self.check.check_verbatimScientificName(self.false_file2), False)

    def test_false_check_verbatimScientificName_two_words(self):
        self.assertEqual(self.check.check_verbatimScientificName(self.false_vsn), False)
    
    def test_check_taxonRank(self):
        self.assertEqual(self.check.check_taxonRank(self.file), True)
    
    def test_false_taxonRank(self):
        self.assertEqual(self.check.check_taxonRank(self.false_file), False)
    
    def test_empty_check_verbatim_associated_taxa(self):
        self.assertEqual(self.check.check_verbatim_associated_taxa(self.false_file2), False)
    
    def test_check_sequence(self):
        self.assertEqual(self.check.check_sequence(self.file), True)
    
    def test_false_check_sequence_one_in_wrong_place(self):
        self.assertEqual(self.check.check_sequence(self.false_file2), False)
    
    def test_false_check_sequence_wrong_number(self):
        self.assertEqual(self.check.check_sequence(self.false_sequence), False)
    
    def test_false_check_sequence_not_numeric(self):
        self.assertEqual(self.check.check_sequence(self.false_vsn), False)
    
    def test_check_false_measumerementValue_according_to_sequence(self):
        self.assertEqual(self.check.check_sequence(self.false_measurement_value), False)
    
    def test_ds_check_measurmentValue(self):
        self.assertEqual(self.check.check_measurementValue(self.file), True)
    
    def test_ds_false_check_measurementValue(self):
        self.assertEqual(self.check.check_measurementValue(self.false_file), False)
    
    def test_pa_check_measurementValue(self):
        self.assertTrue(self.check.check_measurementValue(self.file_pa))

    def test_pa_false_check_measurementValue(self):
        self.assertFalse(self.check.check_measurementValue(self.file_pa_false_measurement_value))
    
    def test_false_check_references(self):
        self.assertEqual(self.check.check_references(self.false_file2, True), False)

    def test_check_all(self):
        self.assertEqual(self.check.check_all_ds(self.file, True), True)
        df = pd.DataFrame.from_dict(self.dict)
        self.assertEqual(self.check.check_all_ds(df, True), True)

    def test_check_all_reference_in_db(self):
        self.assertEqual(self.check.check_all_ds(self.file, False), False)

    def test_check_all_ds_wrong_headers(self):
        df = pd.DataFrame.from_dict({'kirjlaia': ['1111-1111-2222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'moi'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })
        self.assertEqual(self.check.check_all_ds(df, True), False)

    def test_check_all_ds_wrong_author(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'moi'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })
        self.assertEqual(self.check.check_all_ds(df, True), False)

    def test_check_all_ds_missing_verbatim_scientificname(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':["a a a a", 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'moi'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })
        self.assertEqual(self.check.check_all_ds(df, True), False)

    def test_check_all_ds_wrong_taxonrank(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':['sp kapistelija', ' sp kapistelija'], 
        'taxonRank':['laji', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'moi'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })
        self.assertEqual(self.check.check_all_ds(df, True), False)
    
    def test_check_all_ds_empty_verbatim_associated_taxa(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['nan', 'nan'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })
        self.assertEqual(self.check.check_all_ds(df, True), False)

    def test_check_all_ds_wrong_sequence(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'moi'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000']})
        self.assertEqual(self.check.check_all_ds(df, True), False)

    def test_check_all_ds_wrong_measurement_value(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '1111-1111-2222-2233',], 
        'verbatimScientificName':['kapistelifa', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'hello'],
        'sequence':[1,1],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'], 'measurementValue':[0,1] })
        self.assertEqual(self.check.check_all_ds(df, True), False)

    def test_check_all_ds_wrong_reference(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '1111-1111-2222-2233',], 
        'verbatimScientificName':['kapistelifa', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'hello'],
        'sequence':[1,1],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. '], 'measurementValue':[1,1] })
        self.assertEqual(self.check.check_all_ds(df, True), False)
    
    def test_check_all_ds_too_long_verbatim_associated_taxa(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'moi'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })     
        self.assertEqual(self.check.check_all_ds(df, True), False)

    def test_check_all_ds_too_long_line(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '1111-1111-2222-2233'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'habitat':['metsa', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'],
        'verbatimAssociatedTaxa':['moi', 'hello'],
        'sequence':[1,1],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'] })
        self.assertEqual(self.check.check_all_ds(df, True), False)
    
    def test_check_author_not_a_number(self):
        df = pd.DataFrame.from_dict({'author': ['pena-pena-pena-pena', '1111-1111-2222-2233',], 
        'verbatimScientificName':['kapistelifa', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'hello'],
        'sequence':[1,1],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'] })
        self.assertEqual(self.check.check_author(df), False)

    def test_check_verbatiscientificname_is_empty(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '1111-1111-2222-2233'], 
        'verbatimScientificName':['kapistelija',None], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'hello'],
        'sequence':[1,1],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'] })
        self.assertEqual(self.check.check_verbatimScientificName(df), False)
    
    def test_check_verbatiscientificname_is_too_long(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '1111-1111-2222-2233'], 
        'verbatimScientificName':['kapistelija','aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'hello'],
        'sequence':[1,1],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'] })
        self.assertEqual(self.check.check_verbatimScientificName(df), False)

    def test_check_sequence_scientificnames_dont_match(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '1111-1111-2222-2222'], 
        'verbatimScientificName':['pena', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'gei'],
        'sequence':[1,2],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })
        self.assertEqual(self.check.check_sequence(df), False)

    def test_check_sequence_references_dont_match(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-2222', '1111-1111-2222-2222'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'gei'],
        'sequence':[1,2],
        'references':['tosi  tutkimus tm. 2000', 'tosi tieteellinen tutkimus tm. 2000'] })
        self.assertEqual(self.check.check_sequence(df), False)
    
    def test_check_all_ets(self):
        self.assertEqual(self.check.check_all_ets(self.file_ets), True)
        df = pd.DataFrame.from_dict(self.dict_ets)
        self.assertEqual(self.check.check_all_ets(df), True)
#    Test is actually ok but throws "IndexError: invalid index to scalar variable" because of the line "if value[2][0].isalpha() == True or value[2][-1].isalpha() == True:" on check_min_max().

    def test_check_all_ets_wrong_headers(self):
        df = pd.DataFrame.from_dict({'viitteet':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'],
        'verbatimScientificName':['kapistelija', 'kapistelija'],
        'taxonRank':['genus', 'genus'],
        'verbatimTraitName':['body weight (Wt)', 'body weight (Wt)'],
        'verbatimTraitUnit':['kg', 'kg'],
        'author': ['1111-1111-2222-2222', '1111-1111-2222-2233']})
        self.assertEqual(self.check.check_all_ets(df), False)
    
    def test_check_all_ets_wrong_author(self):
        df = pd.DataFrame.from_dict({'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'],
        'verbatimScientificName':['kapistelija', 'kapistelija'],
        'taxonRank':['genus', 'genus'],
        'verbatimTraitName':['body weight (Wt)', 'body weight (Wt)'],
        'verbatimTraitUnit':['kg', 'kg'],
        'author': ['1111-1111-2222-2222', 'abcd-1111-2222-2233']})
        self.assertEqual(self.check.check_all_ets(df), False)

    def test_check_all_ets_missing_werbatim_scientificname(self):
        df = pd.DataFrame.from_dict({'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'],
        'verbatimScientificName':['a a a a', 'kapistelija'],
        'taxonRank':['genus', 'genus'],
        'verbatimTraitName':['body weight (Wt)', 'body weight (Wt)'],
        'verbatimTraitUnit':['kg', 'kg'],
        'author': ['1111-1111-2222-2222', '1111-1111-2222-2233']})
        self.assertEqual(self.check.check_all_ets(df), False)

    def test_check_all_ets_wrong_taxonrank_for_scientificname(self):
        df = pd.DataFrame.from_dict({'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'],
        'verbatimScientificName':['kapistelija', 'kapistelija'],
        'taxonRank':['subspecies', 'subspecies'],
        'verbatimTraitName':['body weight (Wt)', 'body weight (Wt)'],
        'verbatimTraitUnit':['kg', 'kg'],
        'author': ['1111-1111-2222-2222', '1111-1111-2222-2233']})
        self.assertEqual(self.check.check_all_ets(df), False)

    def test_check_all_ets_wrong_taxonrank(self):
        df = pd.DataFrame.from_dict({'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'],
        'verbatimScientificName':['sp kapistelija', 'sp kapistelija'],
        'taxonRank':['subspecies', 'laji'],
        'verbatimTraitName':['body weight (Wt)', 'body weight (Wt)'],
        'verbatimTraitUnit':['kg', 'kg'],
        'author': ['1111-1111-2222-2222', '1111-1111-2222-2233']})
        self.assertEqual(self.check.check_all_ets(df), False)
    
    def test_check_all_ets_too_long_line(self):
        df = pd.DataFrame.from_dict({'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'],
        'verbatimScientificName':['sp kapistelija', 'sp kapistelija'],
        'taxonRank':['subspecies', 'subspecies'],
        'verbatimTraitName':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'body weight (Wt)'],
        'verbatimTraitUnit':['kg', 'kg'],
        'author': ['1111-1111-2222-2222', '1111-1111-2222-2233']})
        self.assertEqual(self.check.check_all_ets(df), False)

    def test_check_all_ets_false_min_max(self):
        df = pd.DataFrame.from_dict({'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'],
        'verbatimScientificName':['kapistelija', 'kapistelija'],
        'taxonRank':['genus', 'genus'],
        'verbatimTraitName':['body weight (Wt)', 'body weight (Wt)'],
        'verbatimTraitUnit':['kg', 'kg'],
        'measurementValue_min':['1', '1'],
        'author': ['1111-1111-2222-2222', '1111-1111-2222-2233']})
        self.assertEqual(self.check.check_all_ets(df), False)

    def test_check_all_pa_wrong_headers(self):
        df = self.pa_df.rename({'verbatimScientificName': 'NIMI', 'author': 'KIRJAILIJA'}, axis=1)
        self.assertEqual(self.check.check_all_pa(df, True), False)

    def test_check_all_pa_wrong_author(self):
        self.pa_df.loc[:, 'author'] = 'ABCD-0000-0001-9627-8821'
        self.assertEqual(self.check.check_all_pa(self.pa_df, True), False)
        self.pa_df.loc[:, 'author'] = '1111-1111-2222-222X'

    def test_check_all_pa_missing_verbatimScientificName(self):
        self.pa_df.loc['0', 'verbatimScientificName'] = 'A A A A'
        self.assertEqual(self.check.check_all_pa(self.pa_df, True), False)
        self.pa_df.loc['0', 'verbatimScientificName'] = 'Grasshoppers: S. gregaria & L. migratoria manilensis'

    def test_check_all_pa_missing_partOfOrganism(self):
        self.pa_df.loc['0', 'PartOfOrganism'] = 'INVALID_PART'
        self.assertEqual(self.check.check_all_pa(self.pa_df, True), False)
        self.pa_df.loc['0', 'PartOfOrganism'] = 'WHOLE'

    def test_check_all_pa_wrong_reference(self):
        self.pa_df.loc['0', 'references'] = 'INVALID_REFERENCE'
        self.assertEqual(self.check.check_all_pa(self.pa_df, True), False)
        self.pa_df.loc['0', 'references'] = 'Suleiman, F.B., Halliru, A. and Adamu, I.T., 2023. Proximate and heavy metal analysis of grasshopper species consumed in Katsina State.'

        def test_check_min_max(self):
        df = pd.DataFrame.from_dict({'measurementValue_min':['2'],
        'measurementValue_max':['3']})
        self.assertEqual(self.check.check_min_max(df), True)
    
    def test_empty_check_min_max(self):
        df = pd.DataFrame.from_dict({'references':['tosi tieteellinen tutkimus tm. 2000']})
        self.assertEqual(self.check.check_min_max(df), False)
    
    def test_only_vtv_check_min_max(self):
        df = pd.DataFrame.from_dict({'verbatimTraitValue':['testi']})
        self.assertEqual(self.check.check_min_max(df), True)
    
    def test_no_max_check_min_max(self):
        df = pd.DataFrame.from_dict({'measurementValue_min':['2']})
        self.assertEqual(self.check.check_min_max(df), False)

    def test_no_min_check_min_max(self):
        df = pd.DataFrame.from_dict({'measurementValue_max':['2']})
        self.assertEqual(self.check.check_min_max(df), False)

    def test_false_check_min_max(self):
        df = pd.DataFrame.from_dict({'measurementValue_min':['3.0'],
        'measurementValue_max':['2.0']})
        self.assertEqual(self.check.check_min_max(df), False)
    
    def test_false_check_min_max_with_mean(self):
        df = pd.DataFrame.from_dict({'measurementValue_min':['3'],
        'measurementValue_max':['2'],
        'verbatimTraitValue':[1]})
        self.assertEqual(self.check.check_min_max(df), False)

    def test_false_mean_check_min_max_compare_to_max(self):
        df = pd.DataFrame.from_dict({'measurementValue_min':['1'],
        'measurementValue_max':['2'],
        'verbatimTraitValue':['3']})
        self.assertEqual(self.check.check_min_max(df), False)

    def test_false_mean_check_min_max_compare_to_min(self):
        df = pd.DataFrame.from_dict({'measurementValue_min':['3'],
        'measurementValue_max':['5'],
        'verbatimTraitValue':['2']})
        self.assertEqual(self.check.check_min_max(df), False)
    
    def test_check_min_max_with_mean_with_characters(self):
        df = pd.DataFrame.from_dict({'verbatimTraitValue':['keskiarvoinen']})
        self.assertEqual(self.check.check_min_max(df), True)
    
    def test_false_check_min_max_with_mean_with_characters(self):
        df = pd.DataFrame.from_dict({'verbatimTraitValue':['keskiarvoinen'],
        'measurementValue_max':['5'],
        'verbatimTraitValue':['2']})
        self.assertEqual(self.check.check_min_max(df), False)

    def test_false_vl_check_lengths(self):
        df = pd.DataFrame.from_dict({'verbatimLocality':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)
    
    def test_false_hab_check_lengths(self):
        df = pd.DataFrame.from_dict({'habitat':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)

    def test_false_se_check_lengths(self):
        df = pd.DataFrame.from_dict({'samplingEffort':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)

    def test_false_ved_check_lengths(self):
        df = pd.DataFrame.from_dict({'verbatimEventDate':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)
    
    def test_false_mm_check_lengths(self):
        df = pd.DataFrame.from_dict({'measurementMethod':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)

    def test_false_ar_check_lengths(self):
        df = pd.DataFrame.from_dict({'associatedReferences':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)

    def test_false_vtn_check_lengths(self):
        df = pd.DataFrame.from_dict({'verbatimTraitName':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)

    def test_false_vtv_check_lengths(self):
        df = pd.DataFrame.from_dict({'verbatimTraitValue':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)

    def test_false_vtu_check_lengths(self):
        df = pd.DataFrame.from_dict({'verbatimTraitUnit':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)

    def test_false_mdb_check_lengths(self):
        df = pd.DataFrame.from_dict({'measurementDeterminedBy':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)

    def test_false_mr_check_lengths(self):
        df = pd.DataFrame.from_dict({'measurementRemarks':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)

    def test_false_ma_check_lengths(self):
        df = pd.DataFrame.from_dict({'measurementAccuracy':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)

    def test_false_sm_check_lengths(self):
        df = pd.DataFrame.from_dict({'statisticalMethod':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)

    def test_false_ls_check_lengths(self):
        df = pd.DataFrame.from_dict({'lifeStage':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)

    def test_false_vla_check_lengths(self):
        df = pd.DataFrame.from_dict({'verbatimLatitude':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)

    def test_false_vlo_check_lengths(self):
        df = pd.DataFrame.from_dict({'verbatimLongitude':['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        self.assertEqual(self.check.check_lengths(df), False)