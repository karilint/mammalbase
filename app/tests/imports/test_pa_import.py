from django.test import TestCase, Client
from django.contrib.messages import get_messages
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount

from mb.models import SourceReference

class ProximateAnalysisImporterTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(username='Testi', password='Testi1234', email='test@test.fi')
        self.client.force_login(self.user)
        self.accountuser = SocialAccount.objects.create(
            uid='1111-1111-2222-2223', user_id=self.user.pk)
        self.reference1 = SourceReference.objects.create(
            citation='Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.')
        self.reference2 = SourceReference.objects.create(
            citation='Creese, S., Davies, S.J. and Bowen, B.J., 2019. Comparative dietary analysis of the black-flanked rock-wallaby (Petrogale lateralis lateralis), the euro (Macropus robustus erubescens) and the feral goat (Capra hircus) from Cape Range National Park, Western Australia. Australian Mammalogy, 41(2), pp.220-230.')

    def test_import_pa_post_correct_file(self):
        with open("tests/imports/assets/pa_true_test.tsv") as fp:
            response = self.client.post(
                '/import/proximate_analysis', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(
            str(messages[0]), "File imported successfully. 1 rows of data were imported. (1 rows were skipped.)")
        self.assertEqual(response.status_code, 302)

    def test_import_pa_post_incorrect_file(self):
        with open("tests/imports/assets/pa_false_test.tsv") as fp:
            response = self.client.post(
                '/import/proximate_analysis', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(
            messages[0]), "Error on row: 1. Error: 'author' field must follow the following format: 0000-0000-0000-0000")
        self.assertEqual(str(
            messages[1]), "Error on row: 2. Error: 'author' field must follow the following format: 0000-0000-0000-0000")
        self.assertEqual(response.status_code, 302)

    def test_import_pa_post_incorrect_file_2(self):
        with open("tests/imports/assets/pa_false_test2.tsv") as fp:
            response = self.client.post(
                '/import/proximate_analysis', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 3)
        self.assertEqual(str(
            messages[0]), "Error on row: 1. Error: 'references' field does not match the RE")
        self.assertEqual(str(
            messages[1]), "Error on row: 2. Error: 'associatedReferences' field does not match the RE")
        self.assertEqual(str(
            messages[2]), "Error on row: 3. Error: 'PartOfOrganism' has invalid value for in rule")
        self.assertEqual(response.status_code, 302)
