from django.test import TestCase
from mb.models import EntityClass, SourceEntity, SourceLocation, SourceMethod
import imports.tools as tools
import tempfile, csv, os
import pandas as pd


class ToolsTest(TestCase):
    def setUp(self):
        with open('test.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['author', 'verbatimScientificName', 'taxonRank', 'verbatimLocality', 'habitat', 'samplingEffort', 'sex', 'individualCount', 'verbatimEventDate', 'measurementMethod', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue', 'associatedReferences',  'references'])
            #rivi 10 mallissa
            writer.writerow(['0000-0001-9627-8821', 'Lagothrix flavicauda', 'Species', '', '', '', '', '', '', '',  'primarily frugivorous', '1','', 'Leo Luna 1980 | deLuycker 2007 | S. Shanee and N. Shanee 2011b | Shanee 2014a | Fack et al. 2018a','Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 11 mallissa
            writer.writerow(['0000-0001-9627-8821', 'Lagothrix flavicauda',	'Species', '', '', '', '', '', '', '',  'leaves', '2', '', 'Leo Luna 1980 | deLuycker 2007 | S. Shanee and N. Shanee 2011b | Shanee 2014a | Fack et al. 2018a', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 17 mallissa
            writer.writerow(['0000-0001-9627-8821',	'Lagothrix flavicauda',	'Species', '', '', '15-month-study', '', '', 'October 2009-June 2010 and August 2010-February 2011', '', 'fruit', '1', '46.3', 'S. Shanee (2014)', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 23 mallissa
            writer.writerow(['0000-0001-9627-8821',	'Lagothrix flavicauda',	'Species',	'', '', '', '', '', '', 'observations of fruit consumption', 'fruits of Ficus',	'1', '43', 'S. Shanee and N. Shanee 2011b',	'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 38 mallissa
            writer.writerow(['0000-0001-9627-8821',	'Capra hircus',	'Species', 'Mandu Mandu Gorge, Cape Range National Park, Western Australia', 'Summer (February, March, April and October)', '', '', '108', 'between February and October 2006', 'The percentage of plant species found in scats.', 'Unidentiﬁed monocots', '1','36.8', 'Original study', 'Creese, S., Davies, S.J. and Bowen, B.J., 2019. Comparative dietary analysis of the black-flanked rock-wallaby (Petrogale lateralis lateralis), the euro (Macropus robustus erubescens) and the feral goat (Capra hircus) from Cape Range National Park, Western Australia. Australian Mammalogy, 41(2), pp.220-230.'])
        with open('false_test.csv', 'w') as file2:
            writer = csv.writer(file2)
            writer.writerow(['writer', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue',  'references'])
            writer.writerow(['0000-0001-9627-8821', 'Lagothrix flavicauda Lagothrix flavicauda', 'Species', 'primarily frugivorous', '1', '', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            writer.writerow(['0000-0001-9627-8821',	'Lagothrix flavicauda',	'animal',	'leaves', '2', '', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            writer.writerow(['0000-0001-9627-8821',	'Lagothrix flavicauda',	'Species',	'fruit', '1', '46.3a','Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])

  
        self.file = pd.read_csv('test.csv')
        self.false_file = pd.read_csv('false_test.csv')
        self.reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][1])
        self.entity = tools.get_entityclass(self.file.loc[:, 'taxonRank'][1])    
        #print(tools.get_entityclass(self.file.loc[:, 'taxonRank'][0]).name)
        #print('Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.')

    def test_check_headers(self):
        self.assertEqual(tools.check_headers(self.file), True)

    def test_check_headers_false(self):
        self.assertEqual(tools.check_headers(self.false_file), False)
    
    def test_check_author(self):
        self.assertEqual(tools.check_author(self.file), True)
    
    def test_check_verbatimScientificName(self):
        self.assertEqual(tools.check_verbatimScientificName(self.file), True)
    
    def test_false_check_verbatimScientificName(self):
        self.assertEqual(tools.check_verbatimScientificName(self.false_file), False)
    
    def test_check_taxonRank(self):
        self.assertEqual(tools.check_taxonRank(self.file), True)
    
    def test_false_taxonRank(self):
        self.assertEqual(tools.check_taxonRank(self.false_file), False)
    
    def test_check_sequence(self):
        self.assertEqual(tools.check_sequence(self.file), True)
    
    def test_check_measurmentValue(self):
        self.assertEqual(tools.check_measurementValue(self.file), True)
    
    def test_false_check_measurementValue(self):
        self.assertEqual(tools.check_measurementValue(self.false_file), False)

    def test_check_all(self):
        self.assertEqual(tools.check_all('', self.file), True)    
    
    def test_new_get_sourcereference_citation(self):
        self.assertEqual(tools.get_sourcereference_citation(self.file.loc[:, 'references'][0]).citation, 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.')

    def test_existing_sourcereference(self):
        self.assertEqual(tools.get_sourcereference_citation(self.reference).citation, 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.')
    
    def test_new_get_entityclass(self):
        self.assertEqual(tools.get_entityclass(self.file.loc[:, 'taxonRank'][0]).name, 'Species')

    def test_existing_entityclass(self):
        self.assertEqual(tools.get_entityclass(self.entity).name, 'Species')

    def test_new_get_sourceentity(self):
        vs_name = self.file.loc[:, 'verbatimScientificName'][0]
        reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][0])
        entityclass = tools.get_entityclass(self.file.loc[:, 'taxonRank'][0])
        self.assertEqual(tools.get_sourceentity(vs_name, reference, entityclass).name, 'Lagothrix flavicauda')
    
    def test_new_get_timeperiod(self):
       reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][2])
       self.assertEqual(tools.get_timeperiod(self.file.loc[:, 'samplingEffort'][2], reference).name, '15-month-study')
    
    def test_new_get_sourcemethod(self):
       reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][3])
       self.assertEqual(tools.get_sourcemethod(self.file.loc[:, 'measurementMethod'][3], reference).name, 'observations of fruit consumption')
    
    def test_new_get_sourcelocation(self):
       reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][4])
       self.assertEqual(tools.get_sourcelocation(self.file.loc[:, 'verbatimLocality'][4], reference).name, 'Mandu Mandu Gorge, Cape Range National Park, Western Australia')        

    def test_nan_to_zero_empty(self):
        self.assertEqual(tools.possible_nan_to_zero(self.file.loc[:, 'individualCount'][4]), 108)

    def test_nan_to_zero(self):
        self.assertEqual(tools.possible_nan_to_zero(self.file.loc[:, 'individualCount'][0]), 0)
    
    def test_nan_to_none_empty(self):
        self.assertEqual(tools.possible_nan_to_none(self.file.loc[:, 'verbatimEventDate'][0]), None)

    def test_nan_to_nan(self):
        self.assertEqual(tools.possible_nan_to_none(self.file.loc[:, 'verbatimEventDate'][2]), 'October 2009-June 2010 and August 2010-February 2011')