from operator import truediv
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import User
from itis.models import TaxonomicUnits, Kingdom, TaxonUnitTypes, SynonymLinks
from allauth.socialaccount.models import SocialAccount
from mb.models.models import EntityClass, MasterReference, SourceAttribute, SourceChoiceSetOption, SourceChoiceSetOptionValue, SourceEntity, SourceLocation, SourceMeasurementValue, SourceMethod, SourceReference, SourceStatistic, TimePeriod, DietSet, FoodItem, DietSetItem, TaxonomicUnits, ChoiceValue
from imports.checker import Check
from decimal import Decimal
import imports.tools as tools
import tempfile, csv, os
import pandas as pd
import numpy as np
import requests_mock

class ToolsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('import/test')
        self.check = Check(self.request)
        self.user = User.objects.create_user(username='Testuser', password='12345')
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        self.reference1 = SourceReference.objects.create(citation='Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.')
        self.reference2 = SourceReference.objects.create(citation='Creese, S., Davies, S.J. and Bowen, B.J., 2019. Comparative dietary analysis of the black-flanked rock-wallaby (Petrogale lateralis lateralis), the euro (Macropus robustus erubescens) and the feral goat (Capra hircus) from Cape Range National Park, Western Australia. Australian Mammalogy, 41(2), pp.220-230.')
        self.accountuser = SocialAccount.objects.create(uid='1111-1111-2222-222X', user_id=self.user.pk)

        setattr(self.request, '_messages', messages)
        with open('test.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['author', 'verbatimScientificName', 'taxonRank', 'verbatimLocality', 'habitat', 'samplingEffort', 'sex', 'individualCount', 'verbatimEventDate', 'measurementMethod', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue', 'associatedReferences',  'references'])
            #rivi 10 mallissa
            writer.writerow(['1111-1111-2222-222X', 'Lagothrix flavicauda', 'Species', '', '', '', '', '', '', '',  'primarily frugivorous', '1','', 'Leo Luna 1980 | deLuycker 2007 | S. Shanee and N. Shanee 2011b | Shanee 2014a | Fack et al. 2018a','Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 11 mallissa
            writer.writerow(['1111-1111-2222-222X', 'Lagothrix flavicauda',	'Species', '', '', '', '', '', '', '',  'leaves', '2', '', 'Leo Luna 1980 | deLuycker 2007 | S. Shanee and N. Shanee 2011b | Shanee 2014a | Fack et al. 2018a', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 17 mallissa
            writer.writerow(['1111-1111-2222-222X',	'Lagothrix flavicauda',	'Species', '', '', '15-month-study', '', '', 'October 2009-June 2010 and August 2010-February 2011', '', 'fruit', '1', '46.3', 'S. Shanee (2014)', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 23 mallissa
            writer.writerow(['1111-1111-2222-222X',	'Lagothrix flavicauda',	'Species',	'', '', '', '', '', '', 'observations of fruit consumption', 'fruits of Ficus',	'1', '43', 'S. Shanee and N. Shanee 2011b',	'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            #rivi 38 mallissa
            writer.writerow(['1111-1111-2222-222X',	'Capra hircus',	'Species', 'Mandu Mandu Gorge, Cape Range National Park, Western Australia', 'Summer (February, March, April and October)', '', '', '108', 'between February and October 2006', 'The percentage of plant species found in scats.', 'Unidentiﬁed monocots', '1','36.8', 'Original study', 'Creese, S., Davies, S.J. and Bowen, B.J., 2019. Comparative dietary analysis of the black-flanked rock-wallaby (Petrogale lateralis lateralis), the euro (Macropus robustus erubescens) and the feral goat (Capra hircus) from Cape Range National Park, Western Australia. Australian Mammalogy, 41(2), pp.220-230.'])
        with open('false_test.csv', 'w') as file2:
            writer = csv.writer(file2)
            writer.writerow(['writer', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue',  'references'])
            writer.writerow(['1111-1111-2222-2222', 'Lagothrix flavicauda Lagothrix flavicauda', 'Species', 'primarily frugivorous', '1', '', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda',	'animal',	'leaves', '2', '', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda',	'Species',	'fruit', '1', '46.3a','Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
        with open('false_measurement_value.csv', 'w') as file3:
            writer = csv.writer(file3)
            writer.writerow(['writer', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue',  'references'])
            writer.writerow(['1111-1111-2222-2222', 'Lagothrix flavicauda Lagothrix flavicauda', 'Species', 'primarily frugivorous', '1', '5', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda',	'animal',	'leaves', '2', '10', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
        with open('false_test2.csv', 'w') as file4:
            writer = csv.writer(file4)
            writer.writerow(['writer', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue',  'references'])
            writer.writerow(['1111-1111-2222-2222', 'Lagothrix flavicauda flavicauda', 'Species', '', '1', '', 'Book'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda flavicauda',	'Species',	'leaves', '2', '',  'Book'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda flavicauda',	'Species',	'fruit', '1', '',   'Book'])
        with open('false_vsn.csv', 'w') as file5:
            writer = csv.writer(file5)
            writer.writerow(['writer', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue',  'references'])
            writer.writerow(['1111-1111-2222-2222', 'Lagothrix flavicauda', 'Genus', 'primarily frugivorous', 'a', '5', 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.'])
        with open('false_sequence.csv', 'w') as file6:
            writer = csv.writer(file6)
            writer.writerow(['writer', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence', 'measurementValue',  'references'])
            writer.writerow(['1111-1111-2222-2222', 'Lagothrix flavicauda flavicauda', 'Species', 'primarily frugivorous', '1', '', 'Book'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda flavicauda',	'Species',	'leaves', '2', '',  'Book'])
            writer.writerow(['1111-1111-2222-2222',	'Lagothrix flavicauda flavicauda',	'Species',	'fruit', '4', '',   'Book'])
        with open('test_ets.csv', 'w') as file7:
            writer = csv.writer(file7)
            writer.writerow(['references', 'verbatimScientificName', 'taxonRank', 'verbatimTraitName', 'verbatimTraitUnit', 'individualCount', 'measurementValue_min', 'measurementValue_max', 'dispersion', 'statisticalMethod', 'verbatimTraitValue', 'sex', 'lifeStage', 'measurementMethod', 'measurementDeterminedBy', 'measurementAccuracy', 'measurementRemarks', 'verbatimLocality', 'author', 'associatedReferences'])
            writer.writerow(['Richard-Hansen, C., Vié, J.C., Vidal, N. and Kéravec, J., 1999. Body measurements on 40 species of mammals from French Guiana. Journal of zoology, 247(4), pp.419-428.', 'Caluromys philander', 'Species', 'body weight (Wt)', 'kg', '22', '0.24', '0.46', '0.06', 'SD', '0.33', 'unknown', '', 'Fleming, T.H., 1991. LH Emmons, & F. Feer 1990. Neotropical rainforest mammals. A field guide. University of Chicago Press, Chicago, xiv+ 281 pages. Hardback: ISBN 0-226-20716-1; Price: UK£ 35.95/US 22.95. Journal of Tropical Ecology, 7(3), pp.400-400.', '', '', '', 'Sinnamary River in French Guiana', '0000-0000-0000-000X', ''])
            writer.writerow(['Richard-Hansen, C., Vié, J.C., Vidal, N. and Kéravec, J., 1999. Body measurements on 40 species of mammals from French Guiana. Journal of zoology, 247(4), pp.419-428.', 'Didelphis albiventris', 'Species', 'body weight (Wt)', 'kg', '24', '0.44', '1.14', '0.18', 'SD', '0.77', 'unknown', '', 'Fleming, T.H., 1991. LH Emmons, & F. Feer 1990. Neotropical rainforest mammals. A field guide. University of Chicago Press, Chicago, xiv+ 281 pages. Hardback: ISBN 0-226-20716-1; Price: UK£ 35.95/US 22.95. Journal of Tropical Ecology, 7(3), pp.400-400.', '', '', '', 'Sinnamary River in French Guiana', '0000-0000-0000-000X', ''])
            writer.writerow(['Richard-Hansen, C., Vié, J.C., Vidal, N. and Kéravec, J., 1999. Body measurements on 40 species of mammals from French Guiana. Journal of zoology, 247(4), pp.419-428.', 'Caluromys philander', 'Species', 'head and body length (HB), tip of nose to inflection point of tail', 'mm', '25', '225', '385', '29', 'SD', '265', 'unknown', '', 'Fleming, T.H., 1991. LH Emmons, & F. Feer 1990. Neotropical rainforest mammals. A field guide. University of Chicago Press, Chicago, xiv+ 281 pages. Hardback: ISBN 0-226-20716-1; Price: UK£ 35.95/US 22.95. Journal of Tropical Ecology, 7(3), pp.400-400.', '', '', '', 'Sinnamary River in French Guiana', '0000-0000-0000-000X', ''])
            writer.writerow(['Richard-Hansen, C., Vié, J.C., Vidal, N. and Kéravec, J., 1999. Body measurements on 40 species of mammals from French Guiana. Journal of zoology, 247(4), pp.419-428.', 'Didelphis albiventris', 'Species', 'head and body length (HB), tip of nose to inflection point of tail', 'mm', '35', '270', '390', '33', 'SD', '334', 'unknown', '', 'Fleming, T.H., 1991. LH Emmons, & F. Feer 1990. Neotropical rainforest mammals. A field guide. University of Chicago Press, Chicago, xiv+ 281 pages. Hardback: ISBN 0-226-20716-1; Price: UK£ 35.95/US 22.95. Journal of Tropical Ecology, 7(3), pp.400-400.', '', '', '', 'Sinnamary River in French Guiana', '0000-0000-0000-000X', ''])
        with open('test_pa.csv', 'w') as file8:
            writer = csv.writer(file8)
            writer.writerow(['verbatimScientificName', 'PartOfOrganism', 'individualCount', 'measurementMethod', 'measurementDeterminedBy', 'verbatimLocality', 'measurementRemarks', 'verbatimEventDate', 'verbatimTraitValue__moisture', 'dispersion__moisture', 'measurementMethod__moisture', 'verbatimTraitValue__dry_matter', 'dispersion__dry_matter', 'measurementMethod__dry_matter', 'verbatimTraitValue__ether_extract', 'dispersion__ether_extract', 'measurementMethod__ether_extract', 'verbatimTraitValue__crude_protein', 'dispersion__crude_protein', 'measurementMethod__crude_protein', 'verbatimTraitValue__crude_fibre', 'dispersion__crude_fibre', 'measurementMethod__crude_fibre', 'verbatimTraitValue_ash', 'dispersion__ash', 'measurementMethod_ash', 'verbatimTraitValue__nitrogen_free_extract', 'dispersion__nitrogen_free_extract', 'measurementMethod__nitrogen_free_extract', 'author', 'associatedReferences', 'references'])
            writer.writerow(['Grasshoppers: S. gregaria & L. migratoria manilensis', 'WHOLE', '', 'Association of the Official Analytical Chemists (AOAC), (1990)', '', 'Sample A/e biological garden Federal College of Education, Katsina State, Nigeria', 'triplicate, wings of the samples were removed before the analysis', '', '5.667', '0.577', 'An atmospheric heat drying at 105 ℃ for 4 h', '', '', '', '10.667', '0.764', 'Soxhlet extraction method', '57.33', '0.148', 'micro Kjeldahl method', '10.333', '0.289', '', '9.833', '0.764', 'direct ashing method at 600 ℃', '6.17', '0.996', '', '1111-1111-2222-222X', 'Original study', 'Suleiman, F.B., Halliru, A. and Adamu, I.T., 2023. Proximate and heavy metal analysis of grasshopper species consumed in Katsina State.'])
            writer.writerow(['Ceratophyllum demersum, whole', 'SHOOT', '','Association of Official Analytical Chemistry (AOAC 2002; AOAC 2002b)', '', 'Köyceğiz – Dalyan Lagoon, Muğla Province, Turkey', 'triplicate', '', '', '', '', '89.57', '', 'oven drying at 105°C for 24 hours', '1.8', '', 'ether extraction method', '15.78', '', 'Kjeldahl protein unit', '18.61', '', '', '18.96', '','firing in a muffle furnace at 550°C for 4 hours', '34.42', '', '', '1111-1111-2222-222X', 'Original study', 'Kiziloğlu, Ü., Yıldırım, Ö. and Çantaş, İ.B., 2023. Use of Coontail as a natural phytoremediation feed additive for common carp. Oceanological and Hydrobiological Studies, 52(1), pp.102-110.'])
            writer.writerow(['Mangifera indica, floral parts', 'FLOWER', '', 'Association of Official Analytical Chemist (AOAC, 1990)', '', 'Ajayi Crowder Memorial Secondary School Bariga, Saint Finberrs Secondary School compound and along same road to Akoka Primary School, Lagos', 'duplicates', '' '12.21', '0.15', '', '5 g sample in an oven at 105 °C for 3 h', '', '', '', '19.5', '1.06', 'petroleum ether extraction in a Soxhlet apparatus, 3 g of sample was extracted for 6 h', '7.2', '0.71', 'Kjeldahl method of 1883', '16.14', '0.15', 'enzymatic gravimetric method used for dietary fibre evaluation (Tecator Fibertec E System Foss Tecator, Sweden', '6.5', '0.35', '4 g in a muffle furnace at 600 °C for 6 h', '38.66', '0.41', 'subtracting the sum of the percent values of moisture, protein, ash, crude fibre, and fat from 100', '1111-1111-2222-222X', 'Original study', 'Adeonipekun, P.A., Adeniyi, T.A., Chidinma, O.Q. and Omolayo, R.O., 2023. Proximate, phytochemical, and antimicrobial evaluation of flowers of Mangifera indica L., stamens of Terminalia catappa L., and anther of Delonix regia (Bojer ex Hook.) Raf. South African Journal of Botany, 155, pp.223-229.'])
            writer.writerow(['Rhynchophorus ferrugineus) larvae', 'LARVAE', '', '', '', 'Yala, Thailand', '', '', '', '', '', '', '', '', '58.8', '0.4', '', '18', '1.2', '', '', '', '', '2.4', '0.1', '', '20.8', '', '', '0000-0001-9627-8821', 'Chinarak et al. (2020)', 'Kavle, R.R., Pritchard, E.T.M., Carne, A., Bekhit, A.E.D.A., Morton, J.D. and Agyei, D., 2023. Nutritional composition and techno-functional properties of sago palm weevil (Rhynchophorus ferrugineus) larvae protein extract. Journal of Asia-Pacific Entomology, p.102086.'])
        with open('test_pa_invalid_headers.csv', 'w') as file9:
            writer = csv.writer(file9)
            writer.writerow(['PartOfOrganism', 'individualCount', 'measurementMethod', 'measurementDeterminedBy', 'verbatimLocality', 'measurementRemarks', 'verbatimEventDate', 'verbatimTraitValue__moisture', 'dispersion__moisture', 'measurementMethod__moisture', 'verbatimTraitValue__dry_matter', 'dispersion__dry_matter', 'measurementMethod__dry_matter', 'verbatimTraitValue__ether_extract', 'dispersion__ether_extract', 'measurementMethod__ether_extract', 'verbatimTraitValue__crude_protein', 'dispersion__crude_protein', 'measurementMethod__crude_protein', 'verbatimTraitValue__crude_fibre', 'dispersion__crude_fibre', 'measurementMethod__crude_fibre', 'verbatimTraitValue_ash', 'dispersion__ash', 'measurementMethod_ash', 'verbatimTraitValue__nitrogen_free_extract', 'dispersion__nitrogen_free_extract', 'measurementMethod__nitrogen_free_extract', 'author', 'associatedReferences', 'references'])
            writer.writerow(['WHOLE', '', 'Association of the Official Analytical Chemists (AOAC), (1990)', '', 'Sample A/e biological garden Federal College of Education, Katsina State, Nigeria', 'triplicate, wings of the samples were removed before the analysis', '', '5.667', '0.577', 'An atmospheric heat drying at 105 ℃ for 4 h', '', '', '', '10.667', '0.764', 'Soxhlet extraction method', '57.33', '0.148', 'micro Kjeldahl method', '10.333', '0.289', '', '9.833', '0.764', 'direct ashing method at 600 ℃', '6.17', '0.996', '', '1111-1111-2222-222X', 'Original study', 'Suleiman, F.B., Halliru, A. and Adamu, I.T., 2023. Proximate and heavy metal analysis of grasshopper species consumed in Katsina State.'])
            writer.writerow(['SHOOT', '','Association of Official Analytical Chemistry (AOAC 2002; AOAC 2002b)', '', 'Köyceğiz – Dalyan Lagoon, Muğla Province, Turkey', 'triplicate', '', '', '', '', '89.57', '', 'oven drying at 105°C for 24 hours', '1.8', '', 'ether extraction method', '15.78', '', 'Kjeldahl protein unit', '18.61', '', '', '18.96', '','firing in a muffle furnace at 550°C for 4 hours	34.42', '', '', '1111-1111-2222-222X', 'Original study', 'Kiziloğlu, Ü., Yıldırım, Ö. and Çantaş, İ.B., 2023. Use of Coontail as a natural phytoremediation feed additive for common carp. Oceanological and Hydrobiological Studies, 52(1), pp.102-110.'])
            writer.writerow(['FLOWER', '', 'Association of Official Analytical Chemist (AOAC, 1990)', '', 'Ajayi Crowder Memorial Secondary School Bariga, Saint Finberrs Secondary School compound and along same road to Akoka Primary School, Lagos', 'duplicates', '' '12.21', '0.15', '', '5 g sample in an oven at 105 °C for 3 h', '', '', '', '19.5', '1.06', 'petroleum ether extraction in a Soxhlet apparatus, 3 g of sample was extracted for 6 h', '7.2', '0.71', 'Kjeldahl method of 1883', '16.14', '0.15', 'enzymatic gravimetric method used for dietary fibre evaluation (Tecator Fibertec E System Foss Tecator, Sweden', '6.5', '0.35', '4 g in a muffle furnace at 600 °C for 6 h', '38.66', '0.41', 'subtracting the sum of the percent values of moisture, protein, ash, crude fibre, and fat from 100', '1111-1111-2222-222X', 'Original study', 'Adeonipekun, P.A., Adeniyi, T.A., Chidinma, O.Q. and Omolayo, R.O., 2023. Proximate, phytochemical, and antimicrobial evaluation of flowers of Mangifera indica L., stamens of Terminalia catappa L., and anther of Delonix regia (Bojer ex Hook.) Raf. South African Journal of Botany, 155, pp.223-229.'])
        with open('test_pa_false_measurement_value.csv', 'w') as file10:
            writer = csv.writer(file10)
            writer.writerow(['verbatimScientificName', 'PartOfOrganism', 'individualCount', 'measurementMethod', 'measurementDeterminedBy', 'verbatimLocality', 'measurementRemarks', 'verbatimEventDate', 'verbatimTraitValue__moisture', 'dispersion__moisture', 'measurementMethod__moisture', 'verbatimTraitValue__dry_matter', 'dispersion__dry_matter', 'measurementMethod__dry_matter', 'verbatimTraitValue__ether_extract', 'dispersion__ether_extract', 'measurementMethod__ether_extract', 'verbatimTraitValue__crude_protein', 'dispersion__crude_protein', 'measurementMethod__crude_protein', 'verbatimTraitValue__crude_fibre', 'dispersion__crude_fibre', 'measurementMethod__crude_fibre', 'verbatimTraitValue_ash', 'dispersion__ash', 'measurementMethod_ash', 'verbatimTraitValue__nitrogen_free_extract', 'dispersion__nitrogen_free_extract', 'measurementMethod__nitrogen_free_extract', 'author', 'associatedReferences', 'references'])
            writer.writerow(['Grasshoppers: S. gregaria & L. migratoria manilensis', 'WHOLE', '', 'Association of the Official Analytical Chemists (AOAC), (1990)', '', 'Sample A/e biological garden Federal College of Education, Katsina State, Nigeria', 'triplicate, wings of the samples were removed before the analysis', '', '5.667', '0.577', 'An atmospheric heat drying at 105 ℃ for 4 h', '', '', '', '10.667', '0.764', 'Soxhlet extraction method', '57.33', '0.148', 'micro Kjeldahl method', '10.333', '0.289', '', '9.833', '0.764', 'direct ashing method at 600 ℃', '6.17', '0.996', '', '1111-1111-2222-222X', 'Original study', 'Suleiman, F.B., Halliru, A. and Adamu, I.T., 2023. Proximate and heavy metal analysis of grasshopper species consumed in Katsina State.'])
            writer.writerow(['Ceratophyllum demersum, whole', 'SHOOT', '','Association of Official Analytical Chemistry (AOAC 2002; AOAC 2002b)', '', 'Köyceğiz – Dalyan Lagoon, Muğla Province, Turkey', 'triplicate', '', '', '', '', '89.57', '', 'oven drying at 105°C for 24 hours', '-1', '', 'ether extraction method', '15.78', '', 'Kjeldahl protein unit', '18.61', '', '', '18.96', '','firing in a muffle furnace at 550°C for 4 hours', '34.42', '', '', '1111-1111-2222-222X', 'Original study', 'Kiziloğlu, Ü., Yıldırım, Ö. and Çantaş, İ.B., 2023. Use of Coontail as a natural phytoremediation feed additive for common carp. Oceanological and Hydrobiological Studies, 52(1), pp.102-110.'])
            writer.writerow(['Mangifera indica, floral parts', 'FLOWER', '', 'Association of Official Analytical Chemist (AOAC, 1990)', '', 'Ajayi Crowder Memorial Secondary School Bariga, Saint Finberrs Secondary School compound and along same road to Akoka Primary School, Lagos', 'duplicates', '' '12.21', '0.15', '', '5 g sample in an oven at 105 °C for 3 h', '', '', '', '19.5', '1.06', 'petroleum ether extraction in a Soxhlet apparatus, 3 g of sample was extracted for 6 h', '7.2', '0.71', 'Kjeldahl method of 1883', '16.14', '0.15', 'enzymatic gravimetric method used for dietary fibre evaluation (Tecator Fibertec E System Foss Tecator, Sweden', '6.5', '0.35', '4 g in a muffle furnace at 600 °C for 6 h', '38.66', '0.41', 'subtracting the sum of the percent values of moisture, protein, ash, crude fibre, and fat from 100', '1111-1111-2222-222X', 'Original study', 'Adeonipekun, P.A., Adeniyi, T.A., Chidinma, O.Q. and Omolayo, R.O., 2023. Proximate, phytochemical, and antimicrobial evaluation of flowers of Mangifera indica L., stamens of Terminalia catappa L., and anther of Delonix regia (Bojer ex Hook.) Raf. South African Journal of Botany, 155, pp.223-229.'])

        self.file = pd.read_csv('test.csv')
        self.file_ets = pd.read_csv('test_ets.csv')
        self.false_file = pd.read_csv('false_test.csv')
        self.false_measurement_value = pd.read_csv('false_measurement_value.csv')
        self.false_file2 = pd.read_csv('false_test2.csv')
        self.false_vsn = pd.read_csv('false_vsn.csv')
        self.false_sequence = pd.read_csv('false_sequence.csv')
        self.file_pa = pd.read_csv('test_pa.csv')
        self.file_pa_invalid_headers = pd.read_csv('test_pa_invalid_headers.csv')
        self.file_pa_false_measurement_value = pd.read_csv('test_pa_false_measurement_value.csv')
        #self.reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][1], self.user)
        self.dict = {'author': ['1111-1111-2222-2222', '1111-1111-2222-2233'], 
        'verbatimScientificName':['kapistelija', 'kapistelija'], 
        'taxonRank':['genus', 'genus'],
        'verbatimAssociatedTaxa':['moi', 'hello'],
        'sequence':[1,1],
        'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'] }
        self.dict_ets = {'references':['tosi tieteellinen tutkimus tm. 2000', 'tosi tieteellinen tm. 2000'],
        'verbatimScientificName':['kapistelija', 'kapistelija'],
        'taxonRank':['genus', 'genus'],
        'verbatimTraitName':['body weight (Wt)', 'body weight (Wt)'],
        'verbatimTraitUnit':['kg', 'kg'],
        'measurementValue_min':['1', '1'],
        'measurementValue_max':['2', '1'],
        'author': ['1111-1111-2222-2222', '1111-1111-2222-2233']}
        self.entity = tools.get_entityclass(self.file.loc[:, 'taxonRank'][1], self.user)

        self.ets_numerical_df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-222X'], 
            'references':['Tester, T., TesterToo, T., Testing, testing'], 
            'taxonRank':['Species'],
            'verbatimScientificName':['Lagothrix flavicauda'],
            'verbatimTraitName':['TestName'],
            'measurementMethod':['SD'],
            'measurementRemarks':['TestRemarks'],
            'verbatimTraitUnit':['km'], 
            'verbatimTraitValue':['5'],
            'verbatimLocality':['TestPlace'],
            'associatedReferences':['TestAssociatedReference'],
            'measurementValue_min':['1'],
            'measurementValue_max':['10'],
            'dispersion':['0.5'],
            'sex':['Female'],
            'lifeStage':['Juvenile'],
            'measurementAccuracy':['0.1'],
            'individualCount':['10']}) 
        self.ets_nonnumerical_df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-222X'], 
            'references':['Tester, T., TesterToo, T., Testing, testing'], 
            'taxonRank':['Species'],
            'verbatimScientificName':['Lagothrix flavicauda'],
            'verbatimTraitName':['TestName'],
            'measurementMethod':[''],
            'measurementRemarks':[''],
            'verbatimTraitUnit':['NA'], 
            'verbatimTraitValue':['TestValues']}) 
        #print(tools.get_entityclass(self.file.loc[:, 'taxonRank'][0]).name)
        #print('Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.')

        self.pa_df = pd.DataFrame.from_dict(
            {
                'verbatimScientificName': ['Grasshoppers: S. gregaria & L. migratoria manilensis','Ceratophyllum demersum, whole','Mangifera indica, floral parts','Rhynchophorus ferrugineus) larvae'],
                'PartOfOrganism':['WHOLE','SHOOT','FLOWER','LARVAE'],
                'individualCount':[np.nan,np.nan,np.nan,np.nan],
                'measurementMethod':['Association of the Official Analytical Chemists (AOAC), (1990)','Association of Official Analytical Chemistry (AOAC 2002; AOAC 2002b)','Association of Official Analytical Chemist (AOAC, 1990)',np.nan],
                'measurementDeterminedBy':[np.nan,np.nan,np.nan,np.nan],
                'verbatimLocality':['Sample A/e biological garden Federal College of Education, Katsina State, Nigeria'
                                    ,'Köyceğiz – Dalyan Lagoon, Muğla Province, Turkey'
                                    ,'Ajayi Crowder Memorial Secondary School Bariga, Saint Finberrs Secondary School compound and along same road to Akoka Primary School, Lagos'
                                    ,'Yala, Thailand'],
                'measurementRemarks':['triplicate, wings of the samples were removed before the analysis','triplicate','duplicates',np.nan],
                'verbatimEventDate':[np.nan,np.nan,np.nan,np.nan],
                'verbatimTraitValue__moisture':[5.667,np.nan,12.21,np.nan],
                'dispersion__moisture':[0.577,np.nan,0.15,np.nan],
                'measurementMethod__moisture':['An atmospheric heat drying at 105 ℃ for 4 h',np.nan,'5 g sample in an oven at 105 °C for 3 h',np.nan],
                'verbatimTraitValue__dry_matter':[np.nan,np.nan,np.nan,np.nan],
                'dispersion__dry_matter':[np.nan,np.nan,np.nan,np.nan],
                'measurementMethod__dry_matter':[np.nan,'oven drying at 105°C for 24 hours',np.nan,np.nan],
                'verbatimTraitValue__ether_extract':[10.667,1.8,19.5,58.8],
                'dispersion__ether_extract':[0.764,np.nan,1.06,0.4],
                'measurementMethod__ether_extract':['Soxhlet extraction method','ether extraction method','petroleum ether extraction in a Soxhlet apparatus, 3 g of sample was extracted for 6 h',np.nan],
                'verbatimTraitValue__crude_protein':[57.33,15.78,7.2,18],
                'dispersion__crude_protein':[0.148,np.nan,0.71,1.2],
                'measurementMethod__crude_protein':['micro Kjeldahl method','Kjeldahl protein unit','Kjeldahl method of 1883',np.nan],
                'verbatimTraitValue__crude_fibre':[10.333,18.61,16.14,np.nan],
                'dispersion__crude_fibre':[0.289,np.nan,0.15,np.nan],
                'measurementMethod__crude_fibre':[np.nan,np.nan,'enzymatic gravimetric method used for dietary fibre evaluation (Tecator Fibertec E System Foss Tecator, Sweden',np.nan],
                'verbatimTraitValue_ash':[9.833,18.96,6.5,2.4],
                'dispersion__ash':[0.764,np.nan,0.35,0.1],
                'measurementMethod_ash':['direct ashing method at 600 ℃','firing in a muffle furnace at 550°C for 4 hours','4 g in a muffle furnace at 600 °C for 6 h',np.nan],
                'verbatimTraitValue__nitrogen_free_extract':[6.17,np.nan,38.66,20.8],
                'dispersion__nitrogen_free_extract':[0.996,np.nan,0.41,np.nan],
                'measurementMethod__nitrogen_free_extract':[np.nan,np.nan,'subtracting the sum of the percent values of moisture, protein, ash, crude fibre, and fat from 100',np.nan],
                'author':['1111-1111-2222-222X','1111-1111-2222-222X','1111-1111-2222-222X','1111-1111-2222-222X'],
                'associatedReferences':['Original study','Original study','Original study','Chinarak et al. (2020)'],
                'references':['Suleiman, F.B., Halliru, A. and Adamu, I.T., 2023. Proximate and heavy metal analysis of grasshopper species consumed in Katsina State.'
                              ,'Kiziloğlu, Ü., Yıldırım, Ö. and Çantaş, İ.B., 2023. Use of Coontail as a natural phytoremediation feed additive for common carp. Oceanological and Hydrobiological Studies, 52(1), pp.102-110.'
                              ,'Adeonipekun, P.A., Adeniyi, T.A., Chidinma, O.Q. and Omolayo, R.O., 2023. Proximate, phytochemical, and antimicrobial evaluation of flowers of Mangifera indica L., stamens of Terminalia catappa L., and anther of Delonix regia (Bojer ex Hook.) Raf. South African Journal of Botany, 155, pp.223-229.'
                              , 'Kavle, R.R., Pritchard, E.T.M., Carne, A., Bekhit, A.E.D.A., Morton, J.D. and Agyei, D., 2023. Nutritional composition and techno-functional properties of sago palm weevil (Rhynchophorus ferrugineus) larvae protein extract. Journal of Asia-Pacific Entomology, p.102086.']
            }
        )

        self.sr = SourceReference.objects.create(citation='Tester, T., TesterToo, T., Testing, testing', status=1)
        self.mr = MasterReference.objects.create(title='Testing, testing', created_by=self.user)
        self.sr_with_mr = SourceReference.objects.create(citation="Title and author", status=2, master_reference=self.mr)
        self.method = SourceMethod.objects.create(reference=self.sr, name='TestMethod')
        self.attribute = SourceAttribute.objects.create(name='SelfAttribute', reference=self.sr, entity=self.entity, method=self.method) 
        self.source_entity = SourceEntity.objects.create(name='Lagothrix flavicauda', reference=self.sr, entity=self.entity)
        self.res = {'status': 'ok', 
                'message-type': 'work-list', 
                'message-version': '1.0.0', 
                'message': {'facets': {}, 'total-results': 2,
                            'items': [
                                        {
                                        'issue': '2', 
                                        'DOI': '10.12345/jott.1234.12.1.12345-12345', 
                                        'type': 'book', 
                                        'created': {'date-parts': [[2022, 2, 26]], 'date-time': '2022-02-26T13:24:30Z', 'timestamp': 1645881870000}, 
                                        'page': '20539-20549',
                                        'title': ['Testing, <i>testing</i>'],
                                        'volume': '20', 
                                        'author': [{'given': 'Teresa', 'family': 'Tester', 'sequence': 'first', 'affiliation': []},
                                                    {'given': 'Timothy', 'family': 'TesterToo', 'sequence': 'additional', 'affiliation': []}], 
                                        'published-online': {'date-parts': [[2022, 2, 26]]}, 
                                        'deposited': {'date-parts': [[2022, 2, 26]], 'date-time': '2022-02-26T13:25:01Z', 'timestamp': 1645881901000}, 
                                        'issued': {'date-parts': [[2022, 2, 26]]}, 
                                        'references-count': 54,
                                        'container-title': ['Testing container-title'], 
                                        'journal-issue': {'issue': '2', 'published-online': {'date-parts': [[2022, 2, 26]]}}, 
                                        'URL': 'http://dx.doi.org/10.11609/jott.6786.14.2.20539-20549', 
                                        'ISSN': ['0974-7907', '0974-7893'], 
                                        'issn-type': [{'value': '0974-7907', 'type': 'electronic'}, {'value': '0974-7893', 'type': 'print'}], 
                                        'published': {'date-parts': [[2022, 2, 26]]}}
                                        ]}, 
                                        'items-per-page': 2, 'query': {'start-index': 0, 'search-terms': None}}
        self.empty_res = {'status': 'ok', 'message-type': 'work-list', 'message-version': '1.0.0', 'message': {'facets': {}, 'total-results': 0, 'items': [], 'items-per-page': 2, 'query': {'start-index': 0, 'search-terms': None}}}
        self.empty_title = {'status': 'ok', 'message-type': 'work-list', 'message-version': '1.0.0', 'message': {'facets': {}, 'total-results': 1, 'items': [{'title': None}], 'items-per-page': 2, 'query': {'start-index': 0, 'search-terms': None}}}
        self.empty_author = {'status': 'ok', 'message-type': 'work-list', 'message-version': '1.0.0', 'message': {'facets': {}, 'total-results': 1, 'items': [{'author': None}], 'items-per-page': 2, 'query': {'start-index': 0, 'search-terms': None}}}
    
    def generate_mock_api(self, m):
        url_dict = {
            'https://www.itis.gov/ITISWebService/jsonservice/getTaxonomicRankNameFromTSN?tsn=18402' : '{"class":"gov.usgs.itis.itis_service.data.SvcTaxonRankInfo","kingdomId":"3","kingdomName":"Plantae","rankId":"180","rankName":"Genus","tsn":"18402"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Mangifera':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["mango"],"nameUsage":"accepted","scientificName":"Mangifera","tsn":"28802"},{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["mango"],"nameUsage":"accepted","scientificName":"Mangifera indica","tsn":"28803"},{"author":"(Stebbing, 1914)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["mango bark beetle"],"nameUsage":"valid","scientificName":"Hypocryphalus mangiferae","tsn":"114931"},{"author":"(Fabricius, 1775)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Sternochetus mangiferae","tsn":"188097"},{"author":"(Green, 1889)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Protopulvinaria mangiferae","tsn":"200874"},{"author":"Blanco","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["pahutan"],"nameUsage":"accepted","scientificName":"Mangifera altissima","tsn":"506471"},{"author":"Jack","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["binjai"],"nameUsage":"accepted","scientificName":"Mangifera caesia","tsn":"506472"},{"author":"Lour.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["bachang"],"nameUsage":"accepted","scientificName":"Mangifera foetida","tsn":"506473"},{"author":"Griff.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["kwini"],"nameUsage":"accepted","scientificName":"Mangifera odorata","tsn":"506474"},{"author":"Cotes, 1893","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Dacus ferrugineus var. mangiferae","tsn":"676634"},{"author":"Austin, 1984","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Synopeas mangiferae","tsn":"733051"},{"author":"Lesne, 1921","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Dinoderus mangiferae","tsn":"817533"},{"author":"Chûjô, 1936","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Sinoxylon mangiferae","tsn":"817723"},{"author":"Workman, 1896","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Cheiracanthium mangiferae","tsn":"875934"}],"requestedName":"Mangifera"}',
            'https://www.itis.gov/ITISWebService/jsonservice/getFullHierarchyFromTSN?tsn=28802':'{"author":"","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecordList","hierarchyList":[{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"","parentTsn":"","rankName":"Kingdom","taxonName":"Plantae","tsn":"202422"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Plantae","parentTsn":"202422","rankName":"Subkingdom","taxonName":"Viridiplantae","tsn":"954898"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Viridiplantae","parentTsn":"954898","rankName":"Infrakingdom","taxonName":"Streptophyta","tsn":"846494"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Streptophyta","parentTsn":"846494","rankName":"Superdivision","taxonName":"Embryophyta","tsn":"954900"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Embryophyta","parentTsn":"954900","rankName":"Division","taxonName":"Tracheophyta","tsn":"846496"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Tracheophyta","parentTsn":"846496","rankName":"Subdivision","taxonName":"Spermatophytina","tsn":"846504"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Spermatophytina","parentTsn":"846504","rankName":"Class","taxonName":"Magnoliopsida","tsn":"18063"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Magnoliopsida","parentTsn":"18063","rankName":"Superorder","taxonName":"Rosanae","tsn":"846548"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Rosanae","parentTsn":"846548","rankName":"Order","taxonName":"Sapindales","tsn":"28643"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Sapindales","parentTsn":"28643","rankName":"Family","taxonName":"Anacardiaceae","tsn":"28771"},{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Anacardiaceae","parentTsn":"28771","rankName":"Genus","taxonName":"Mangifera","tsn":"28802"},{"author":"Blanco","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Mangifera","parentTsn":"28802","rankName":"Species","taxonName":"Mangifera altissima","tsn":"506471"},{"author":"Jack","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Mangifera","parentTsn":"28802","rankName":"Species","taxonName":"Mangifera caesia","tsn":"506472"},{"author":"Lour.","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Mangifera","parentTsn":"28802","rankName":"Species","taxonName":"Mangifera foetida","tsn":"506473"},{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Mangifera","parentTsn":"28802","rankName":"Species","taxonName":"Mangifera indica","tsn":"28803"},{"author":"Griff.","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Mangifera","parentTsn":"28802","rankName":"Species","taxonName":"Mangifera odorata","tsn":"506474"}],"rankName":"","sciName":"","tsn":"28802"}',
            'https://www.itis.gov/ITISWebService/jsonservice/getTaxonomicRankNameFromTSN?tsn=28802':'{"class":"gov.usgs.itis.itis_service.data.SvcTaxonRankInfo","kingdomId":"3","kingdomName":"Plantae","rankId":"180","rankName":"Genus","tsn":"28802"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Rhynchophorus':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"Herbst, 1795","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Rhynchophorus","tsn":"114819"},{"author":"(Linnaeus, 1758)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Rhynchophorus palmarum","tsn":"114820"},{"author":"(Fabricius, 1775)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Rhynchophorus cruentatus","tsn":"618909"},{"author":"Say, 1831","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Rhynchophorus cicatricosus","tsn":"620082"},{"author":"Erichson, 1847","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Rhynchophorus cycadis","tsn":"620083"},{"author":"Chevrolat, 1880","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Rhynchophorus depressus","tsn":"620084"},{"author":"Say, 1831","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Rhynchophorus immunis","tsn":"620085"},{"author":"Chevrolat, 1880","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Rhynchophorus lanuginosus","tsn":"620086"},{"author":"Say, 1831","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Rhynchophorus placidus","tsn":"620087"},{"author":"Say, 1831","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Rhynchophorus praepotens","tsn":"620088"},{"author":"Say, 1831","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Rhynchophorus truncatus","tsn":"620089"},{"author":"Fahraeus, 1845","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Rhynchophorus zimmermanni","tsn":"620090"},{"author":"(Boulenger, 1898)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Campylomormyrus rhynchophorus","tsn":"649829"},{"author":"Fain, 1974","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Curculanoetus rhynchophorus","tsn":"1188219"}],"requestedName":"Rhynchophorus"}',
            'https://www.itis.gov/ITISWebService/jsonservice/getFullHierarchyFromTSN?tsn=114819':'{"author":"","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecordList","hierarchyList":[{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"","parentTsn":"","rankName":"Kingdom","taxonName":"Animalia","tsn":"202423"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Animalia","parentTsn":"202423","rankName":"Subkingdom","taxonName":"Bilateria","tsn":"914154"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Bilateria","parentTsn":"914154","rankName":"Infrakingdom","taxonName":"Protostomia","tsn":"914155"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Protostomia","parentTsn":"914155","rankName":"Superphylum","taxonName":"Ecdysozoa","tsn":"914158"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Ecdysozoa","parentTsn":"914158","rankName":"Phylum","taxonName":"Arthropoda","tsn":"82696"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Arthropoda","parentTsn":"82696","rankName":"Subphylum","taxonName":"Hexapoda","tsn":"563886"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Hexapoda","parentTsn":"563886","rankName":"Class","taxonName":"Insecta","tsn":"99208"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Insecta","parentTsn":"99208","rankName":"Subclass","taxonName":"Pterygota","tsn":"100500"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Pterygota","parentTsn":"100500","rankName":"Infraclass","taxonName":"Neoptera","tsn":"563890"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Neoptera","parentTsn":"563890","rankName":"Superorder","taxonName":"Holometabola","tsn":"914213"},{"author":"Linnaeus, 1758","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Holometabola","parentTsn":"914213","rankName":"Order","taxonName":"Coleoptera","tsn":"109216"},{"author":"Emery, 1886","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Coleoptera","parentTsn":"109216","rankName":"Suborder","taxonName":"Polyphaga","tsn":"112747"},{"author":"Lameere, 1938","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Polyphaga","parentTsn":"112747","rankName":"Infraorder","taxonName":"Cucujiformia","tsn":"678305"},{"author":"Latreille, 1802","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Cucujiformia","parentTsn":"678305","rankName":"Superfamily","taxonName":"Curculionoidea","tsn":"114654"},{"author":"Latreille, 1802","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Curculionoidea","parentTsn":"114654","rankName":"Family","taxonName":"Curculionidae","tsn":"114666"},{"author":"Schönherr, 1825","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Curculionidae","parentTsn":"114666","rankName":"Subfamily","taxonName":"Dryophthorinae","tsn":"678828"},{"author":"Herbst, 1795","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Dryophthorinae","parentTsn":"678828","rankName":"Genus","taxonName":"Rhynchophorus","tsn":"114819"},{"author":"(Fabricius, 1775)","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Rhynchophorus","parentTsn":"114819","rankName":"Species","taxonName":"Rhynchophorus cruentatus","tsn":"618909"},{"author":"(Linnaeus, 1758)","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Rhynchophorus","parentTsn":"114819","rankName":"Species","taxonName":"Rhynchophorus palmarum","tsn":"114820"}],"rankName":"","sciName":"","tsn":"114819"}',
            'https://www.itis.gov/ITISWebService/jsonservice/getTaxonomicRankNameFromTSN?tsn=114819':'{"class":"gov.usgs.itis.itis_service.data.SvcTaxonRankInfo","kingdomId":"5","kingdomName":"Animalia","rankId":"180","rankName":"Genus","tsn":"114819"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Grasshoppers':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["grasshoppers"],"nameUsage":"valid","scientificName":"Orthoptera","tsn":"102160"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["pygmy grasshoppers"],"nameUsage":"valid","scientificName":"Tetrigidae","tsn":"102162"},{"author":"Burr, 1898","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["monkey grasshoppers"],"nameUsage":"valid","scientificName":"Eumastacidae","tsn":"102191"},{"author":"MacLeay, 1819","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["grasshoppers","short-horned grasshoppers"],"nameUsage":"valid","scientificName":"Acrididae","tsn":"102195"},{"author":"Krauss, 1902","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["long-horned grasshoppers"],"nameUsage":"valid","scientificName":"Tettigoniidae","tsn":"102232"},{"author":"Thunberg, 1815","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["smaller meadow grasshoppers"],"nameUsage":"valid","scientificName":"Conocephalus","tsn":"102249"},{"author":"Blanchard, 1845","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["wingless long-horned grasshoppers"],"nameUsage":"valid","scientificName":"Gryllacrididae","tsn":"102278"}],"requestedName":"Grasshoppers"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Grasshoppers%20gregaria' : '{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[null],"requestedName":"Grasshoppers gregaria"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Taraxacum%20officinale':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"F.H. Wigg.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["dandelion","blowball","faceclock","common dandelion"],"nameUsage":"accepted","scientificName":"Taraxacum officinale","tsn":"36213"},{"author":"(Ledeb.) Schinz ex Thell.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["common dandelion","rough dandelion","fleshy dandelion","horned dandelion"],"nameUsage":"not accepted","scientificName":"Taraxacum officinale ssp. ceratophorum","tsn":"524741"},{"author":"F.H. Wigg.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["wandering dandelion","common dandelion","lesser hawkbit"],"nameUsage":"accepted","scientificName":"Taraxacum officinale ssp. officinale","tsn":"524742"},{"author":"(Lam.) Schinz & R. Keller","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["common dandelion"],"nameUsage":"not accepted","scientificName":"Taraxacum officinale ssp. vulgare","tsn":"524743"},{"author":"(Lyons) Blytt","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Taraxacum officinale var. palustre","tsn":"541136"}],"requestedName":"Taraxacum officinale"}',
            'https://www.itis.gov/ITISWebService/jsonservice/getFullHierarchyFromTSN?tsn=36213':'{"author":"","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecordList","hierarchyList":[{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"","parentTsn":"","rankName":"Kingdom","taxonName":"Plantae","tsn":"202422"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Plantae","parentTsn":"202422","rankName":"Subkingdom","taxonName":"Viridiplantae","tsn":"954898"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Viridiplantae","parentTsn":"954898","rankName":"Infrakingdom","taxonName":"Streptophyta","tsn":"846494"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Streptophyta","parentTsn":"846494","rankName":"Superdivision","taxonName":"Embryophyta","tsn":"954900"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Embryophyta","parentTsn":"954900","rankName":"Division","taxonName":"Tracheophyta","tsn":"846496"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Tracheophyta","parentTsn":"846496","rankName":"Subdivision","taxonName":"Spermatophytina","tsn":"846504"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Spermatophytina","parentTsn":"846504","rankName":"Class","taxonName":"Magnoliopsida","tsn":"18063"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Magnoliopsida","parentTsn":"18063","rankName":"Superorder","taxonName":"Asteranae","tsn":"846535"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Asteranae","parentTsn":"846535","rankName":"Order","taxonName":"Asterales","tsn":"35419"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Asterales","parentTsn":"35419","rankName":"Family","taxonName":"Asteraceae","tsn":"35420"},{"author":"F.H. Wigg.","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Asteraceae","parentTsn":"35420","rankName":"Genus","taxonName":"Taraxacum","tsn":"36199"},{"author":"F.H. Wigg.","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Taraxacum","parentTsn":"36199","rankName":"Species","taxonName":"Taraxacum officinale","tsn":"36213"},{"author":"F.H. Wigg.","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Taraxacum officinale","parentTsn":"36213","rankName":"Subspecies","taxonName":"Taraxacum officinale ssp. officinale","tsn":"524742"}],"rankName":"","sciName":"","tsn":"36213"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Voikukka':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[null],"requestedName":"Voikukka"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Galipea%20officinalis':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"Hanc.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["Angostura tree"],"nameUsage":"not accepted","scientificName":"Galipea officinalis","tsn":"506391"}],"requestedName":"Galipea officinalis"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Oxya%20japonica':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"(Thunberg, 1815,","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["Japanese grasshopper"],"nameUsage":"invalid","scientificName":"Oxya japonica","tsn":"102221"}],"requestedName":"Oxya japonica"}',
            'https://www.itis.gov/ITISWebService/jsonservice/getAcceptedNamesFromTSN?tsn=102221':'{"acceptedNames":[{"acceptedName":"Oxya velox","acceptedTsn":"650544","author":"(Fabricius, 1787,","class":"gov.usgs.itis.itis_service.data.SvcAcceptedName"}],"class":"gov.usgs.itis.itis_service.data.SvcAcceptedNameList","tsn":"102221"}',
            'https://www.itis.gov/ITISWebService/jsonservice/getFullHierarchyFromTSN?tsn=650544':'{"author":"","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecordList","hierarchyList":[{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"","parentTsn":"","rankName":"Kingdom","taxonName":"Animalia","tsn":"202423"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Animalia","parentTsn":"202423","rankName":"Subkingdom","taxonName":"Bilateria","tsn":"914154"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Bilateria","parentTsn":"914154","rankName":"Infrakingdom","taxonName":"Protostomia","tsn":"914155"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Protostomia","parentTsn":"914155","rankName":"Superphylum","taxonName":"Ecdysozoa","tsn":"914158"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Ecdysozoa","parentTsn":"914158","rankName":"Phylum","taxonName":"Arthropoda","tsn":"82696"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Arthropoda","parentTsn":"82696","rankName":"Subphylum","taxonName":"Hexapoda","tsn":"563886"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Hexapoda","parentTsn":"563886","rankName":"Class","taxonName":"Insecta","tsn":"99208"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Insecta","parentTsn":"99208","rankName":"Subclass","taxonName":"Pterygota","tsn":"100500"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Pterygota","parentTsn":"100500","rankName":"Infraclass","taxonName":"Neoptera","tsn":"563890"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Neoptera","parentTsn":"563890","rankName":"Superorder","taxonName":"Polyneoptera","tsn":"914215"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Polyneoptera","parentTsn":"914215","rankName":"Order","taxonName":"Orthoptera","tsn":"102160"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Orthoptera","parentTsn":"102160","rankName":"Suborder","taxonName":"Caelifera","tsn":"102161"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Caelifera","parentTsn":"102161","rankName":"Infraorder","taxonName":"Acrididea","tsn":"657454"},{"author":"MacLeay, 1819","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Acrididea","parentTsn":"657454","rankName":"Superfamily","taxonName":"Acridoidea","tsn":"650497"},{"author":"MacLeay, 1819","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Acridoidea","parentTsn":"650497","rankName":"Family","taxonName":"Acrididae","tsn":"102195"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Acrididae","parentTsn":"102195","rankName":"Subfamily","taxonName":"Oxyinae","tsn":"650537"},{"author":"Serville, 1831","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Oxyinae","parentTsn":"650537","rankName":"Genus","taxonName":"Oxya","tsn":"102220"},{"author":"(Fabricius, 1787,","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Oxya","parentTsn":"102220","rankName":"Species","taxonName":"Oxya velox","tsn":"650544"}],"rankName":"","sciName":"","tsn":"650544"}',
            'https://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Taraxacum%20officinale':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"F.H. Wigg.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["dandelion","blowball","faceclock","common dandelion"],"nameUsage":"accepted","scientificName":"Taraxacum officinale","tsn":"36213"},{"author":"(Ledeb., Schinz ex Thell.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["common dandelion","rough dandelion","fleshy dandelion","horned dandelion"],"nameUsage":"not accepted","scientificName":"Taraxacum officinale ssp. ceratophorum","tsn":"524741"},{"author":"F.H. Wigg.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["wandering dandelion","common dandelion","lesser hawkbit"],"nameUsage":"accepted","scientificName":"Taraxacum officinale ssp. officinale","tsn":"524742"},{"author":"(Lam., Schinz & R. Keller","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["common dandelion"],"nameUsage":"not accepted","scientificName":"Taraxacum officinale ssp. vulgare","tsn":"524743"},{"author":"(Lyons, Blytt","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Taraxacum officinale var. palustre","tsn":"541136"}],"requestedName":"Taraxacum officinale"}',
            'https://www.itis.gov/ITISWebService/jsonservice/getAcceptedNamesFromTSN?tsn=61653':'{"acceptedNames":[{"acceptedName":"Marilynia macrodentata","acceptedTsn":"61652","author":"(Wieser, 1959,","class":"gov.usgs.itis.itis_service.data.SvcAcceptedName"}],"class":"gov.usgs.itis.itis_service.data.SvcAcceptedNameList","tsn":"61653"}',
            'https://www.itis.gov/ITISWebService/jsonservice/getFullHierarchyFromTSN?tsn=61652':'{"author":"","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecordList","hierarchyList":[{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"","parentTsn":"","rankName":"Kingdom","taxonName":"Animalia","tsn":"202423"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Animalia","parentTsn":"202423","rankName":"Subkingdom","taxonName":"Bilateria","tsn":"914154"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Bilateria","parentTsn":"914154","rankName":"Infrakingdom","taxonName":"Protostomia","tsn":"914155"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Protostomia","parentTsn":"914155","rankName":"Superphylum","taxonName":"Ecdysozoa","tsn":"914158"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Ecdysozoa","parentTsn":"914158","rankName":"Phylum","taxonName":"Nematoda","tsn":"59490"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Nematoda","parentTsn":"59490","rankName":"Class","taxonName":"Chromadorea","tsn":"914188"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Chromadorea","parentTsn":"914188","rankName":"Subclass","taxonName":"Chromadoria","tsn":"59492"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Chromadoria","parentTsn":"59492","rankName":"Order","taxonName":"Desmodorida","tsn":"60662"},{"author":"Filipjev, 1918","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Desmodorida","parentTsn":"60662","rankName":"Family","taxonName":"Cyatholaimidae","tsn":"61479"},{"author":"Hopper, 1972","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Cyatholaimidae","parentTsn":"61479","rankName":"Genus","taxonName":"Marilynia","tsn":"61648"},{"author":"(Wieser, 1959,","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Marilynia","parentTsn":"61648","rankName":"Species","taxonName":"Marilynia macrodentata","tsn":"61652"}],"rankName":"","sciName":"","tsn":"61652"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Gregaria':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"Donkin","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"accepted","scientificName":"Navicula gregaria","tsn":"3860"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"accepted","scientificName":"Chlamydomonas gregaria","tsn":"5451"},{"author":"(A. Heller) McNeill","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["brittle sandwort"],"nameUsage":"not accepted","scientificName":"Minuartia nuttallii ssp. gregaria","tsn":"20007"},{"author":"E.P. Bicknell","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Sanicula gregaria","tsn":"29853"},{"author":"(L. Agassiz, 1862)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Clytia gregaria","tsn":"49604"},{"author":"G. O. Sars, 1885","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Thysanoessa gregaria","tsn":"95572"},{"author":"Fischer von Waldheim, 1820","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Nebria gregaria","tsn":"109489"},{"author":"Gagne, 1981","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Endaphis gregaria","tsn":"125280"},{"author":"Melander, 1902","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Hilara congregaria","tsn":"136067"},{"author":"(Frick, 1954)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Chromatomyia gregaria","tsn":"143867"},{"author":"Frick, 1954","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Phytomyza gregaria","tsn":"143868"},{"author":"(Lesson, 1830)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Paramolgula gregaria","tsn":"159627"},{"author":"Lesson, 1830","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Cynthia gregaria","tsn":"159628"},{"author":"(Lesson, 1830)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Molgula gregaria","tsn":"159629"},{"author":"(Heller, 1867)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Gregarinidra gregaria","tsn":"201350"},{"author":"Heller, 1867","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Membranipora gregaria","tsn":"201351"},{"author":"(G. O. Sars, 1892)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Proboloides gregaria","tsn":"206566"},{"author":"A. Heller","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Arenaria gregaria","tsn":"509050"},{"author":"(A. Heller) Maguire","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Arenaria nuttallii ssp. gregaria","tsn":"525264"},{"author":"(A. Heller) Jeps.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Arenaria nuttallii var. gregaria","tsn":"532241"},{"author":"(Mitt.) R.H. Zander","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"accepted","scientificName":"Barbula indica var. gregaria","tsn":"549337"},{"author":"Warncke, 1974","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Andrena gregaria","tsn":"752445"},{"author":"(Schrottky, 1905)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Hypanthidioides gregaria","tsn":"755970"},{"author":"Pedro and Camargo, 2003","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Partamona gregaria","tsn":"763967"},{"author":"(Warncke, 1992)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Hoplitis benoisti gregaria","tsn":"768026"},{"author":"Boiss. & Heldr.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Vicia gregaria","tsn":"820766"},{"author":"(Boiss. & Heldr.) P.H. Davis","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"accepted","scientificName":"Vicia canescens ssp. gregaria","tsn":"820833"},{"author":"(A. Heller) Rabeler & R.L. Hartm.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["brittle sandwort"],"nameUsage":"accepted","scientificName":"Minuartia nuttallii var. gregaria","tsn":"823698"},{"author":"(Weise, 1905)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Chiridopsis gregaria","tsn":"840272"},{"author":"(Brause) Domin","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"accepted","scientificName":"Cyathea gregaria","tsn":"914374"},{"author":"Brause","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Alsophila gregaria","tsn":"915203"},{"author":"(W. Fox, 1898)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Mimesa gregaria","tsn":"1016716"},{"author":"(Malloch, 1933)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Mimesa gregaria simplex","tsn":"1018049"},{"author":"Lange-Bertalot and U. Rumrich in U. Rumrich, Lange-Bertalot and Rumrich","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"accepted","scientificName":"Navicula supergregaria","tsn":"1020505"},{"author":"Marloth","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"accepted","scientificName":"Euphorbia gregaria","tsn":"1026541"},{"author":"(Marloth) P.V. Heath","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Tirucalia gregaria","tsn":"1031577"},{"author":"Delève, 1963","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Pseudelmidolia gregaria","tsn":"1064962"},{"author":"Colenso","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"accepted","scientificName":"Fossombronia gregaria","tsn":"1108968"},{"author":"(Hook.f. & Taylor) Gottsche, Lindenb. & Nees","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"accepted","scientificName":"Plagiochila gregaria","tsn":"1113513"},{"author":"Geoffroy, 1762","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Apis gregaria","tsn":"1128082"},{"author":"Mitt.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Tortula gregaria","tsn":"1136058"},{"author":"(Schrank, 1781)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Microgaster gregaria","tsn":"1144346"},{"author":"Warncke, 1992","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Osmia benoisti gregaria","tsn":"1165582"},{"author":"(Fabricius, 1793)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Munida gregaria","tsn":"1201726"},{"author":"Fabricius, 1793","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Galathea gregaria","tsn":"1202153"},{"author":"(Fabricius, 1793)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Grimothea gregaria","tsn":"1202377"}],"requestedName":"Gregaria"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Gregaria%20migratoria':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[null],"requestedName":"Gregaria migratoria"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Migratoria':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"Hartert, 1903","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["Yellow-billed Grosbeak","Chinese Grosbeak"],"nameUsage":"valid","scientificName":"Eophona migratoria","tsn":"559921"},{"author":"Hartert, 1903","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Eophona migratoria migratoria","tsn":"729555"},{"author":"Riley, 1915","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Eophona migratoria sowerbyi","tsn":"729556"},{"author":"Linnaeus, 1766","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Columba migratoria","tsn":"1125301"},{"author":"Nadchatram and Wilson, 1969","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Mackiena migratoria","tsn":"1179427"},{"author":"Abo-Shnaf in Abo-Shnaf et al., 2020","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Blattisocius migratoriae","tsn":"1184428"}],"requestedName":"Migratoria"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Migratoria%20manilensis':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[null],"requestedName":"Migratoria manilensis"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Manilensis':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"Philippi","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["asian clam"],"nameUsage":"valid","scientificName":"Corbicula manilensis","tsn":"81386"},{"author":"(Marion de Procé, 1822)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["striped puffer"],"nameUsage":"valid","scientificName":"Arothron manilensis","tsn":"553408"},{"author":"Herre, 1923","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Ophichthus manilensis","tsn":"636119"},{"author":"Ashmead, 1905","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Macroteleia manilensis","tsn":"751193"},{"author":"Meyen, 1834","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Ardea purpurea manilensis","tsn":"824406"},{"author":"(Weise, 1910)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Malayocassis manilensis","tsn":"840345"},{"author":"(Weise, 1910)","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"valid","scientificName":"Agoniella manilensis","tsn":"842163"},{"author":"Schultze, 1915","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Trox manilensis","tsn":"929963"},{"author":"Rohwer, 1910","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Notogonidea manilensis","tsn":"1010236"},{"author":"Marion de Procé, 1822","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Tetrodon manilensis","tsn":"1054798"},{"author":"Martens, 1876","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"invalid","scientificName":"Varanus manilensis","tsn":"1204402"}],"requestedName":"Manilensis"}',
            'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=Ceratophyllum':'{"class":"gov.usgs.itis.itis_service.data.SvcItisTermList","itisTerms":[{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["hornwort"],"nameUsage":"accepted","scientificName":"Ceratophyllum","tsn":"18402"},{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["coon\'s-tail","coontail","hornwort","common hornwort","coon\'s tail"],"nameUsage":"accepted","scientificName":"Ceratophyllum demersum","tsn":"18403"},{"author":"Cham.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["prickly hornwort"],"nameUsage":"accepted","scientificName":"Ceratophyllum muricatum","tsn":"18404"},{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["soft hornwort"],"nameUsage":"accepted","scientificName":"Ceratophyllum submersum","tsn":"18405"},{"author":"Michx.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["threadfoot","podostémon à feuilles cornées","hornleaf riverweed"],"nameUsage":"accepted","scientificName":"Podostemum ceratophyllum","tsn":"27031"},{"author":"A. Gray","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["spineless hornwort"],"nameUsage":"accepted","scientificName":"Ceratophyllum echinatum","tsn":"501366"},{"author":"Cham.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ceratophyllum apiculatum","tsn":"510606"},{"author":"Griseb.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ceratophyllum australe","tsn":"510607"},{"author":"Spruce ex K. Schum.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ceratophyllum cristatum","tsn":"510608"},{"author":"Fassett","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["Florida hornwort"],"nameUsage":"not accepted","scientificName":"Ceratophyllum floridanum","tsn":"510609"},{"author":"Fassett","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ceratophyllum llerenae","tsn":"510610"},{"author":"(Griseb.) Les","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":["prickly hornwort"],"nameUsage":"accepted","scientificName":"Ceratophyllum muricatum ssp. australe","tsn":"523836"},{"author":"auct. non (Cham.) Wilmot-Dear","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ceratophyllum submersum ssp. muricatum","tsn":"525442"},{"author":"(Cham.) Asch.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ceratophyllum demersum var. apiculatum","tsn":"533317"},{"author":"(Cham.) Garcke","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ceratophyllum demersum var. apiculatum","tsn":"533318"},{"author":"K. Schum.","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ceratophyllum demersum var. cristatum","tsn":"533319"},{"author":"(A. Gray) A. Gray","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ceratophyllum demersum var. echinatum","tsn":"533320"},{"author":"(A. Gray) Wilmot-Dear","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ceratophyllum submersum var. echinatum","tsn":"533321"},{"author":"(Cham.) Wilmot-Dear","class":"gov.usgs.itis.itis_service.data.SvcItisTerm","commonNames":[null],"nameUsage":"not accepted","scientificName":"Ceratophyllum submersum ssp. muricatum","tsn":"897269"}],"requestedName":"Ceratophyllum"}',
            'https://www.itis.gov/ITISWebService/jsonservice/getFullHierarchyFromTSN?tsn=18402':'{"author":"","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecordList","hierarchyList":[{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"","parentTsn":"","rankName":"Kingdom","taxonName":"Plantae","tsn":"202422"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Plantae","parentTsn":"202422","rankName":"Subkingdom","taxonName":"Viridiplantae","tsn":"954898"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Viridiplantae","parentTsn":"954898","rankName":"Infrakingdom","taxonName":"Streptophyta","tsn":"846494"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Streptophyta","parentTsn":"846494","rankName":"Superdivision","taxonName":"Embryophyta","tsn":"954900"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Embryophyta","parentTsn":"954900","rankName":"Division","taxonName":"Tracheophyta","tsn":"846496"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Tracheophyta","parentTsn":"846496","rankName":"Subdivision","taxonName":"Spermatophytina","tsn":"846504"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Spermatophytina","parentTsn":"846504","rankName":"Class","taxonName":"Magnoliopsida","tsn":"18063"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Magnoliopsida","parentTsn":"18063","rankName":"Superorder","taxonName":"Ceratophyllanae","tsn":"846540"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Ceratophyllanae","parentTsn":"846540","rankName":"Order","taxonName":"Ceratophyllales","tsn":"846616"},{"author":null,"class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Ceratophyllales","parentTsn":"846616","rankName":"Family","taxonName":"Ceratophyllaceae","tsn":"18401"},{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Ceratophyllaceae","parentTsn":"18401","rankName":"Genus","taxonName":"Ceratophyllum","tsn":"18402"},{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Ceratophyllum","parentTsn":"18402","rankName":"Species","taxonName":"Ceratophyllum demersum","tsn":"18403"},{"author":"A. Gray","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Ceratophyllum","parentTsn":"18402","rankName":"Species","taxonName":"Ceratophyllum echinatum","tsn":"501366"},{"author":"Cham.","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Ceratophyllum","parentTsn":"18402","rankName":"Species","taxonName":"Ceratophyllum muricatum","tsn":"18404"},{"author":"L.","class":"gov.usgs.itis.itis_service.data.SvcHierarchyRecord","parentName":"Ceratophyllum","parentTsn":"18402","rankName":"Species","taxonName":"Ceratophyllum submersum","tsn":"18405"}],"rankName":"","sciName":"","tsn":"18402"}',

        }
        for url, data in url_dict.items():
            m.get(url,text=data)

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

    @requests_mock.Mocker()
    def test_pa_check_cf_valid(self, m):
        self.generate_mock_api(m)
        df = self.pa_df.copy()
        self.assertTrue(self.check.check_cf_valid(df))
        df.at[1, 'verbatimTraitValue__crude_fibre'] = np.nan
        self.assertFalse(self.check.check_cf_valid(df))

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

    def test_new_get_sourcereference_citation(self):
        self.assertEqual(tools.get_sourcereference_citation(self.file.loc[:, 'references'][0], self.user).citation, 'Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.')

    def test_get_sourcereference_citation_with_existing_masterreference(self):
        old_sr = tools.get_sourcereference_citation('Title and author', self.user)
        self.assertEqual(old_sr, self.sr_with_mr)

    def test_new_get_entityclass(self):
        self.assertEqual(tools.get_entityclass(self.file.loc[:, 'taxonRank'][0], self.user).name, 'Species')

    def test_existing_entityclass(self):
        self.assertEqual(tools.get_entityclass(self.entity, self.user).name, 'Species')

    def test_new_get_sourceentity(self):
        vs_name = self.file.loc[:, 'verbatimScientificName'][0]
        #reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][0], self.user)
        entityclass = tools.get_entityclass(self.file.loc[:, 'taxonRank'][0], self.user)
        #self.assertEqual(tools.get_sourceentity(vs_name, reference, entityclass, self.user).name, 'Lagothrix flavicauda')
        self.assertEqual(tools.get_sourceentity(vs_name, self.sr, entityclass, self.user).name, 'Lagothrix flavicauda')
    
    def test_new_get_timeperiod(self):
       #reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][2], self.user)
       #self.assertEqual(tools.get_timeperiod(self.file.loc[:, 'samplingEffort'][2], reference, self.user).name, '15-month-study')
       self.assertEqual(tools.get_timeperiod(self.file.loc[:, 'samplingEffort'][2], self.sr, self.user).name, '15-month-study')
    
    def test_new_get_sourcemethod(self):
       #reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][3], self.user)
       #self.assertEqual(tools.get_sourcemethod(self.file.loc[:, 'measurementMethod'][3], reference, self.user).name, 'observations of fruit consumption')
        self.assertEqual(tools.get_sourcemethod(self.file.loc[:, 'measurementMethod'][3], self.sr, self.user).name, 'observations of fruit consumption')

    def test_new_get_sourcelocation(self):
       #reference = tools.get_sourcereference_citation(self.file.loc[:, 'references'][4], self.user)
       self.assertEqual(tools.get_sourcelocation(self.file.loc[:, 'verbatimLocality'][4], self.sr, self.user).name, 'Mandu Mandu Gorge, Cape Range National Park, Western Australia')        
        #self.assertEqual(tools.get_sourcelocation(self.file.loc[:, 'verbatimLocality'][4], reference, self.user).name, 'Mandu Mandu Gorge, Cape Range National Park, Western Australia')        

    def test_nan_to_zero_empty(self):
        self.assertEqual(tools.possible_nan_to_zero(self.file.loc[:, 'individualCount'][4]), 108)

    def test_nan_to_zero(self):
        self.assertEqual(tools.possible_nan_to_zero(self.file.loc[:, 'individualCount'][0]), 0)
    
    def test_nan_to_none_empty(self):
        self.assertEqual(tools.possible_nan_to_none(self.file.loc[:, 'verbatimEventDate'][0]), None)

    def test_nan_to_nan(self):
        self.assertEqual(tools.possible_nan_to_none(self.file.loc[:, 'verbatimEventDate'][2]), 'October 2009-June 2010 and August 2010-February 2011')

    def test_trims_whitespace(self):
        df = pd.DataFrame.from_dict({'author': ['    1111-1111-2222-2222', '0000-0001-9627-8821'], 
        'verbatimScientificName':['kapistelija', 'kapistelija    '], 
        'taxonRank':['genus', 'genus'],
        'references':['tosi tieteellinen tutkimus    tm. 2000', 'tosi tieteellinen tutkimus tm.'] })
        tools.trim_df(df)
        self.assertEqual(df.at[0, 'author'],'1111-1111-2222-2222' )
        self.assertEqual(df.at[1, 'verbatimScientificName'],'kapistelija' )
        self.assertEqual(df.at[0, 'references'],'tosi tieteellinen tutkimus tm. 2000' )

    def test_create_masterreference(self):
        answer = tools.create_masterreference('Tester, T., TesterToo, T., Testing, testing', self.res, self.sr, self.user)
        self.assertEquals(answer, True)

    def test_create_masterreference_saves_correct_info(self):
        tools.create_masterreference('Tester, T., TesterToo, T., Testing, testing', self.res, self.sr, self.user)
        sourceref = SourceReference.objects.filter(citation='Tester, T., TesterToo, T., Testing, testing')[0]
        mr = sourceref.master_reference
        self.assertEqual(mr.title, 'Testing, testing')
        self.assertEqual(mr.first_author, 'Tester, T.')
        self.assertEqual(mr.doi, '10.12345/jott.1234.12.1.12345-12345')
        self.assertEqual(mr.type, 'book')
        self.assertEqual(mr.uri, None)
        self.assertEqual(mr.year, 2022)
        self.assertEqual(mr.container_title, 'Testing container-title')
        self.assertEqual(mr.volume, 20)
        self.assertEqual(mr.issue, '2')
        self.assertEqual(mr.page, '20539-20549')
        self.assertEqual(mr.citation, 'Tester, T., TesterToo, T. 2022. Testing, testing. Available at: 10.12345/jott.1234.12.1.12345-12345.')
        self.assertEqual(mr.created_by, self.user)

    def test_create_masterreference_with_wrong_title(self):
        answer = tools.create_masterreference('Tester, T., TesterToo, T., Testing, not testing at all', self.res, self.sr, self.user)
        self.assertEquals(answer, False)

    def test_create_masterreference_empty(self):
        answer = tools.create_masterreference('Tester, T., TesterToo, T., Testing, testing', self.empty_res, self.sr, self.user)
        self.assertEquals(answer, False)
    
    def test_create_masterreference_without_title(self):
        answer = tools.create_masterreference('Tester, T., TesterToo, T., Testing, testing', self.empty_title, self.sr, self.user)
        self.assertEquals(answer, False)
    
    def test_create_masterreference_without_author(self):
        answer = tools.create_masterreference('Tester, T., TesterToo, T., Testing, testing', self.empty_author, self.sr, self.user)
        self.assertEquals(answer, False)

    def test_title_matches_citation_correct(self):
        answer = tools.title_matches_citation('<i>This is          a correct title  \n          </i>', 'This is a correct title')
        self.assertEquals(answer, True)
    
    def test_title_matches_citation_false(self):
        answer = tools.title_matches_citation('This is not a correct title', 'This is a correct title')
        self.assertEquals(answer, False)

    def test_make_harvard_citation_journalarticle(self):
        test_citation = tools.make_harvard_citation_journalarticle('Testing, testing', 'doi123', ['Tester, T.', 'TesterToo, T.', 'TesterThree, T.'],
                                                                        '2022', 'Testing container-title', '20', '2', '123-321')
        self.assertEquals('Tester, T., TesterToo, T., TesterThree, T. 2022. Testing, testing. Testing container-title. 20(2), pp.123-321. Available at: doi123.', test_citation)
    
    def test_get_existing_fooditem(self):
        food_item = FoodItem(name='TEST', part=None, tsn=None, pa_tsn=None, is_cultivar=0)
        food_item.save()
        result = tools.get_fooditem('TEST', None)
        self.assertEqual(result.name, 'TEST')
    
    @requests_mock.Mocker()
    def test_get_fooditem_json(self, m):
        self.generate_mock_api(m)
        results = tools.get_fooditem_json('TARAXACUM OFFICINALE')
        self.assertEqual(results['data'][0]['results'][0]['taxon_id'], '36213')
    
    @requests_mock.Mocker()
    def test_false_get_fooditem_json(self, m):
        self.generate_mock_api(m)
        results = tools.get_fooditem_json('VOIKUKKA')
        self.assertRaises(KeyError, lambda: results['data'][0]['results'])
    
    @requests_mock.Mocker()
    def test_invalid_get_fooditem_json(self, m):
        self.generate_mock_api(m)
        results = tools.get_fooditem_json('GALIPEA OFFICINALIS')
        self.assertEqual(results['data'][0]['results'][0]['taxonomic_status'], 'not accepted')
        results = tools.get_fooditem_json('OXYA JAPONICA')
        self.assertEqual(results['data'][0]['results'][0]['taxonomic_status'], 'invalid')
    
    @requests_mock.Mocker()
    def test_get_accepted_tsn(self, m):
        self.generate_mock_api(m)
        results = tools.get_accepted_tsn(102221)
        self.assertEqual(results['data'][0]['results'][0]['taxon_id'], '650544')
    
    @requests_mock.Mocker()
    def test_create_fooditem(self, m):
        self.generate_mock_api(m)
        test_results = {'data':{0:{'results': {0:
                        {'canonical_form': 'Taraxacum officinale',
                        'classification_path': 'Plantae|Viridiplantae|Streptophyta|Embryophyta|Tracheophyta|Spermatophytina|Magnoliopsida|Asteranae|Asterales|Asteraceae|Taraxacum|Taraxacum officinale',
                        'classification_path_ranks': 'Kingdom|Subkingdom|Infrakingdom|Superdivision|Division|Subdivision|Class|Superorder|Order|Family|Genus|Species',
                        'classification_path_ids': 	'202422|954898|846494|954900|846496|846504|18063|846535|35419|35420|36199|36213',
                        'taxon_id':'36213',
                        'taxonomic_status':'accepted'}}}}}
        kingdom = Kingdom(pk = 3, name = 'Plantae')
        kingdom.save()
        rank = TaxonUnitTypes(rank_id = 220, rank_name = 'Species', kingdom_id = 3, dir_parent_rank_id = 190,req_parent_rank_id = 180)
        rank.save()
        food_item = tools.create_fooditem(test_results, 'TARAXACUM OFFICINALE', None)
        self.assertEqual(food_item.tsn.tsn, 36213)


    def test_get_sourcestatistic_existing(self):
        source_statistic = SourceStatistic(name='Test statistic', reference=self.sr, created_by=self.user)
        source_statistic.save()
        result = tools.get_sourcestatistic('Test statistic', self.sr, self.user)
        self.assertEqual(result.name, 'Test statistic')

    def test_get_sourcestatistic_new(self):
        new_sr = SourceReference(citation='New sourcereference, 2000')
        new_sr.save()
        source_statistic = tools.get_sourcestatistic('Test statistic two', new_sr, self.user)
        result = source_statistic.reference
        self.assertEqual(result.citation, 'New sourcereference, 2000')
        self.assertEqual(source_statistic.name, 'Test statistic two')

    def test_no_nans_are_saved(self):
        df = pd.DataFrame.from_dict({'samplingEffort': ['   '], 
        'sex':[' '], 
        'individualCount':[''],
        'associatedReferences':[''],
        'samplingEffort':[''],
        'measurementMethod':[''],
        'verbatimEventDate':[''],
             })
        tools.trim_df(df)

        time_period = tools.get_timeperiod(df.loc[:, 'samplingEffort'][0], self.sr, self.user)
        gender = tools.get_choicevalue(df.loc[:, 'sex'][0])
        gender_ets = tools.get_choicevalue_ets(df.loc[:, 'sex'][0], 'gender', self.user)
        sample_size = tools.possible_nan_to_zero(df.loc[:, 'individualCount'][0])
        cited_reference = tools.possible_nan_to_none(df.loc[:, 'associatedReferences'][0])
        method = tools.get_sourcemethod(df.loc[:, 'measurementMethod'][0], self.sr, self.user)
        self.assertNotEqual(time_period.name, 'nan')
        self.assertNotEqual(type(gender), ChoiceValue)
        self.assertEqual(gender_ets.caption, '')
        self.assertNotEqual(sample_size, 0.0)
        self.assertNotEqual(cited_reference, 'nan')
        self.assertNotEqual(method.name, 'nan')
        self.assertEqual(method.name, '')

    def test_get_sourcechoicesetoption_and_value(self):
        scso = tools.get_sourcechoicesetoption('TestName', self.attribute, self.user)
        self.assertEqual(scso.name, 'TestName')
        self.assertEqual(scso.created_by.username, 'Testuser')
        scsov = tools.get_sourcechoicesetoptionvalue(self.source_entity, scso, self.user)
        self.assertEqual(scsov.source_choiceset_option, scso)
        self.assertEqual(scsov.source_entity.name, 'Lagothrix flavicauda')
        self.assertEqual(scsov.created_by.username, 'Testuser')

    def test_get_sourceattribute_na(self):
        attribute = tools.get_sourceattribute('TestAttribute', self.sr, self.entity, self.method, 2, self.user)
        self.assertEqual(attribute.name, 'TestAttribute')
        self.assertEqual(attribute.created_by.username, 'Testuser')

    def test_get_author(self):
        self.assertEqual(tools.get_author('1111-1111-2222-222X'), self.user)

    def test_valid_author(self):
        self.assertEqual(self.check.check_valid_author(self.file), True)
    
    def test_empty_valid_author(self):
        df = pd.DataFrame.from_dict({'author': ['nan'] })
        self.assertEqual(self.check.check_valid_author(df), False)

    def test_create_ets_numerical(self):
        df = self.ets_numerical_df
        tools.trim_df(df)
        headers =  list(df.columns.values)
        for row in df.itertuples():
            tools.create_ets(row, headers)
        smv = SourceMeasurementValue.objects.get(measurement_accuracy=0.1)
        self.assertEqual(smv.source_entity.name, 'Lagothrix flavicauda')
        self.assertEqual(smv.n_male, 0)
        self.assertEqual(smv.n_unknown, 0)
        self.assertEqual(smv.n_female, 10)
        self.assertEqual(smv.n_total, 10)
        
    def test_create_ets_nonnumerical(self):
        df = self.ets_nonnumerical_df
        tools.trim_df(df)   
        headers =  list(df.columns.values)
        for row in df.itertuples():
            tools.create_ets(row, headers)
        sa = SourceAttribute.objects.get(name='TestName')
        self.assertEqual(sa.type, 2)
        cso = SourceChoiceSetOption.objects.get(source_attribute=sa)
        self.assertEqual(cso.name, 'TestValues')
        csov = SourceChoiceSetOptionValue.objects.get(source_choiceset_option=cso)
        self.assertEqual(csov.source_entity.name, 'Lagothrix flavicauda')

    def test_create_ets_minimum_headers(self):
        df = pd.DataFrame.from_dict({'author': ['1111-1111-2222-222X'], 
            'references':['Tester, T., TesterToo, T., Testing, testing'],
            'taxonRank':['Species'],
            'verbatimScientificName':['Lagothrix flavicauda'],
            'verbatimTraitName':['TestName'],
            'verbatimTraitUnit':['km'], 
            'verbatimTraitValue':[4.2]}) 

        tools.trim_df(df)
        headers =  list(df.columns.values)
        for row in df.itertuples():
            tools.create_ets(row, headers)
        sa = SourceAttribute.objects.get(name='TestName')
        smv = SourceMeasurementValue.objects.get(source_attribute=sa)
        self.assertEqual(smv.source_entity.name, 'Lagothrix flavicauda')
        self.assertEqual(smv.n_total, 0)
    
    def test_check_nfe(self):
        df_missing_nfe_headers = pd.DataFrame.from_dict(
            {
                'verbatimScientificName': ['Grasshoppers: S. gregaria & L. migratoria manilensis','Ceratophyllum demersum, whole','Mangifera indica, floral parts'],
                'PartOfOrganism':['WHOLE','SHOOT','FLOWER'],
                'individualCount':[np.nan,np.nan,np.nan],
                'measurementMethod':['Association of the Official Analytical Chemists (AOAC), (1990)','Association of Official Analytical Chemistry (AOAC 2002; AOAC 2002b)','Association of Official Analytical Chemist (AOAC, 1990)'],
                'measurementDeterminedBy':[np.nan,np.nan,np.nan],
                'verbatimLocality':['Sample A/e biological garden Federal College of Education, Katsina State, Nigeria','Köyceğiz – Dalyan Lagoon, Muğla Province, Turkey','Ajayi Crowder Memorial Secondary School Bariga, Saint Finberrs Secondary School compound and along same road to Akoka Primary School, Lagos'],
                'measurementRemarks':['triplicate, wings of the samples were removed before the analysis','triplicate','duplicates'],
                'verbatimEventDate':[np.nan,np.nan,np.nan],
                'verbatimTraitValue__moisture':[5.667,np.nan,12.21],
                'dispersion__moisture':[0.577,np.nan,0.15],
                'measurementMethod__moisture':['An atmospheric heat drying at 105 ℃ for 4 h',np.nan,'5 g sample in an oven at 105 °C for 3 h'],
                'verbatimTraitValue__dry_matter':[np.nan,np.nan,np.nan,],
                'dispersion__dry_matter':[np.nan,np.nan,np.nan],
                'measurementMethod__dry_matter':[np.nan,'oven drying at 105°C for 24 hours',np.nan],
                'verbatimTraitValue__ether_extract':[10.667,1.8,19.5],
                'dispersion__ether_extract':[0.764,np.nan, 1.06],
                'measurementMethod__ether_extract':['Soxhlet extraction method','ether extraction method', 'petroleum ether extraction in a Soxhlet apparatus, 3 g of sample was extracted for 6 h'],
                'verbatimTraitValue__crude_protein':[57.33,15.78,7.2],
                'dispersion__crude_protein':[0.148,np.nan,0.71],
                'measurementMethod__crude_protein':['micro Kjeldahl method','Kjeldahl protein unit','Kjeldahl method of 1883'],
                'verbatimTraitValue__crude_fibre':[10.333,18.61,16.14],
                'dispersion__crude_fibre':[0.289,np.nan,0.15],
                'measurementMethod__crude_fibre':[np.nan,np.nan,'enzymatic gravimetric method used for dietary fibre evaluation (Tecator Fibertec E System Foss Tecator, Sweden'],
                'verbatimTraitValue_ash':[9.833,18.96,6.5],
                'dispersion__ash':[0.764,np.nan,0.35],
                'measurementMethod_ash':['direct ashing method at 600 ℃','firing in a muffle furnace at 550°C for 4 hours','4 g in a muffle furnace at 600 °C for 6 h'],
                'author':['1111-1111-2222-222X','1111-1111-2222-222X','1111-1111-2222-222X'],
                'associatedReferences':['Original study','Original study','Original study',],
                'references':['Suleiman, F.B., Halliru, A. and Adamu, I.T., 2023. Proximate and heavy metal analysis of grasshopper species consumed in Katsina State.','Kiziloğlu, Ü., Yıldırım, Ö. and Çantaş, İ.B., 2023. Use of Coontail as a natural phytoremediation feed additive for common carp. Oceanological and Hydrobiological Studies, 52(1), pp.102-110.','Adeonipekun, P.A., Adeniyi, T.A., Chidinma, O.Q. and Omolayo, R.O., 2023. Proximate, phytochemical, and antimicrobial evaluation of flowers of Mangifera indica L., stamens of Terminalia catappa L., and anther of Delonix regia (Bojer ex Hook.) Raf. South African Journal of Botany, 155, pp.223-229.']
            }
        )
        df = df_missing_nfe_headers.copy()
        df['verbatimTraitValue__nitrogen_free_extract'] = [6.17, np.nan, 38.45]
        df['measurementMethod__nitrogen_free_extract'] = [np.nan, np.nan, 'subtracting the sum of the percent values of moisture, protein, ash, crude fibre, and fat from 100']
        df['dispersion__nitrogen_free_extract'] = [np.nan, np.nan, np.nan]
        df_template = df.copy()
        
        df_template.at[1, 'verbatimTraitValue__nitrogen_free_extract'] = 44.85
        df_template.at[1, 'measurementMethod__nitrogen_free_extract'] = "\nNot reported: calculated by difference"
        self.assertTrue(self.check.check_nfe(df))
        self.assertTrue(df.to_string(), df_template.to_string())
        self.assertTrue(self.check.check_nfe(df_missing_nfe_headers))
        df_missing_nfe_headers.sort_index(axis=1, inplace=True)
        df_template.sort_index(axis=1, inplace=True)
        df_template['measurementMethod__nitrogen_free_extract'] = "\nNot reported: calculated by difference"
        self.assertEqual(df_missing_nfe_headers.to_string(), df_template.to_string())
        

    def test_convert_empty_values_pa(self):
        df = self.pa_df.copy()
        df.loc[:] = np.nan
        pa_item_dict = {
            "proximate_analysis" : None,
            "location" : None,
            "cited_reference" : None,
            "forage" : None
        }
        headers = list(df.columns.values)
        template_headers = [
            "proximate_analysis",
            "location",
            "cited_reference",
            "forage",
            "sample_size",
            "measurement_determined_by",
            "measurement_remarks",
            "moisture_reported",
            "moisture_dispersion",
            "moisture_measurement_method",
            "dm_reported",
            "dm_dispersion",
            "dm_measurement_method",
            "ee_reported",
            "ee_dispersion",
            "ee_measurement_method",
            "cp_reported",
            "cp_dispersion",
            "cp_measurement_method",
            "cf_reported",
            "cf_dispersion",
            "cf_measurement_method",
            "ash_reported",
            "ash_dispersion",
            "ash_measurement_method",
            "nfe_reported",
            "nfe_dispersion",
            "nfe_measurement_method",
            "cited_reference"
        ]
        for row in df.itertuples():
            new_item_dict = tools.convert_empty_values_pa(row=row, headers=headers, pa_item_dict=pa_item_dict)
            self.assertEqual(template_headers.sort(), list(new_item_dict.keys()).sort())
            self.assertTrue('nan' not in new_item_dict.values() and np.nan not in new_item_dict.values())
            for item in new_item_dict.values():
                self.assertTrue(item == None)

    def test_check_generate_standard_values_pa(self):
        reported_values = {
            'moisture_reported':[12.21, None, 39.1],
            'dm_reported':[None, None, 960.9],
            'ee_reported':[19.5, 58.8, 27.1],
            'cp_reported':[7.2, 18, 580.7],
            'cf_reported':[16.14, None, 83.3],
            'ash_reported':[6.5, 2.4, 250.4],
            'nfe_reported':[38.66, 20.8, 19.4]
        }
        expected_values = {
            'ee_std':[Decimal(19.459), Decimal(58.8), Decimal(2.71)],
            'cp_std':[Decimal(7.185), Decimal(18), Decimal(58.07)],
            'cf_std':[Decimal(16.106), None, Decimal(8.33)],
            'ash_std':[Decimal(6.486), Decimal(2.4), Decimal(25.04)],
            'nfe_std':[Decimal(38.579), Decimal(20.8), Decimal(1.94)]
        }

        # Test generated standard values for each row in reported_values separately
        for row in range(len(reported_values['moisture_reported'])):
            # Generate standard values for current row
            reported = {}
            for header in reported_values:
                reported[header] = reported_values[header][row]
            std_values = tools.generate_standard_values_pa(reported)
            # Test standard values for current row
            for header in std_values:
                if 'reported' in header:
                    self.assertAlmostEqual(reported_values[header][row], std_values[header], 3)
                elif 'std' in header:
                    self.assertAlmostEqual(expected_values[header][row], std_values[header], 3)
    
    def test_create_tsn(self):
        test_data = {
        'taxon_id': '26655',
        'canonical_form': 'Delonix',
        'classification_path_ids': '202422-954898-846494-954900-846496-846504-18063-846548-500022-500059-26655',
        'classification_path': 'Plantae-Viridiplantae-Streptophyta-Embryophyta-Tracheophyta-Spermatophytina-Magnoliopsida-Rosanae-Fabales-Fabaceae-Delonix',
        'classification_path_ranks': 'Kingdom-Subkingdom-Infrakingdom-Superdivision-Division-Subdivision-Class-Superorder-Order-Family-Genus',
        'taxonomic_status':'accepted'
        }
        kingdom = Kingdom(name=test_data['classification_path'].split('-')[0])
        kingdom.save()
        rank = TaxonUnitTypes(rank_name=test_data['classification_path_ranks'].split('-')[-1], kingdom_id=kingdom.pk, rank_id=0, dir_parent_rank_id=0, req_parent_rank_id=0)
        rank.save()
        taxonomic_unit = tools.create_tsn({'data': [{'results': [test_data]}]}, int(test_data['taxon_id']))
        self.assertEqual(type(taxonomic_unit),TaxonomicUnits)
        query = TaxonomicUnits.objects.filter(tsn=int(test_data['taxon_id']))
        self.assertTrue(len(query)>0)
        self.assertEqual(query[0].tsn, int(test_data['taxon_id']))
        self.assertEqual(query[0].completename, test_data['canonical_form'])
        self.assertEqual(query[0].hierarchy_string, test_data['classification_path_ids'])
        self.assertEqual(query[0].hierarchy, test_data['classification_path'])
        self.assertEqual(query[0].kingdom_id, kingdom.pk)
        self.assertEqual(query[0].rank_id, rank.pk)
    

    @requests_mock.Mocker()
    def test_create_tsn_invalid(self, m):
        self.generate_mock_api(m)

        invalid_test_data = {
        'taxon_id': '61653',
        'canonical_form': 'Choniolaimus macrodentatus',
        'classification_path_ids': '',
        'classification_path': '',
        'classification_path_ranks': '',
        'taxonomic_status':'invalid'
        }
        valid_test_data = {
        'taxon_id': '61652',
        'canonical_form': 'Marilynia macrodentata',
        'classification_path_ids': '202423-914154-914155-914158-59490-914188-59492-60662-61479-61648-61652',
        'classification_path': 'Animalia-Bilateria-Protostomia-Ecdysozoa-Nematoda-Chromadorea-Chromadoria-Desmodorida-Cyatholaimidae-Marilynia-Marilynia macrodentata',
        'classification_path_ranks': 'Kingdom-Subkingdom-Infrakingdom-Superphylum-Phylum-Class-Subclass-Order-Family-Genus-Species',
        'taxonomic_status':'valid'
        }
        kingdom = Kingdom(name=valid_test_data['classification_path'].split('-')[0])
        kingdom.save()
        rank = TaxonUnitTypes(rank_name=valid_test_data['classification_path_ranks'].split('-')[-1], kingdom_id=kingdom.pk, rank_id=0, dir_parent_rank_id=0, req_parent_rank_id=0)
        rank.save()
        taxonomic_unit = tools.create_tsn({'data': [{'results': [invalid_test_data]}]}, int(invalid_test_data['taxon_id']))
        self.assertEqual(type(taxonomic_unit),TaxonomicUnits)
        query = TaxonomicUnits.objects.filter(tsn=int(invalid_test_data['taxon_id']))
        self.assertTrue(len(query)>0)
        self.assertEqual(query[0].tsn, int(invalid_test_data['taxon_id']))
        self.assertEqual(query[0].completename, invalid_test_data['canonical_form'])
        self.assertEqual(query[0].hierarchy_string, valid_test_data['classification_path_ids'])
        self.assertEqual(query[0].hierarchy, valid_test_data['classification_path'])
        self.assertEqual(query[0].kingdom_id, kingdom.pk)
        self.assertEqual(query[0].rank_id, rank.pk)

        query_valid = TaxonomicUnits.objects.filter(tsn=int(valid_test_data['taxon_id']))
        self.assertTrue(len(query_valid)>0)
        self.assertEqual(query_valid[0].tsn, int(valid_test_data['taxon_id']))
        self.assertEqual(query_valid[0].completename, valid_test_data['canonical_form'])
        self.assertEqual(query_valid[0].hierarchy_string, valid_test_data['classification_path_ids'])
        self.assertEqual(query_valid[0].hierarchy, valid_test_data['classification_path'])
        self.assertEqual(query_valid[0].kingdom_id, kingdom.pk)
        self.assertEqual(query_valid[0].rank_id, rank.pk)

        sl_q = SynonymLinks.objects.filter(tsn=query[0])
        self.assertTrue(len(sl_q)>0)
        self.assertEqual(sl_q[0].tsn_accepted, query_valid[0])
        self.assertEqual(sl_q[0].tsn_accepted_name, query_valid[0].completename)
