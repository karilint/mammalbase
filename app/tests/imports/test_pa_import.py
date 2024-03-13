from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
import tempfile, csv, os
from allauth.socialaccount.models import SocialAccount
import imports.views as views
import pandas as pd
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from allauth.socialaccount.models import SocialAccount
from mb.models.models import EntityClass, MasterReference, SourceAttribute, SourceEntity, SourceMethod, SourceReference, SourceStatistic, TimePeriod, DietSet, FoodItem, DietSetItem, TaxonomicUnits, ChoiceValue, MasterEntity
from mb.models.location_models import SourceLocation
from itis.models import Kingdom, TaxonUnitTypes
import tempfile, csv, os
import pandas as pd
import json
import requests_mock
from unittest import skip


class ProximateAnalysisImporterTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(username='Testi')
        self.client.force_login(self.user)
        self.accountuser = SocialAccount.objects.create(uid='1111-1111-2222-222X', user_id=self.user.pk)
        self.reference1 = SourceReference.objects.create(citation='Serrano-Villavicencio, J.E., Shanee, S. and Pacheco, V., 2021. Lagothrix flavicauda (Primates: Atelidae). Mammalian Species, 53(1010), pp.134-144.')
        self.reference2 = SourceReference.objects.create(citation='Creese, S., Davies, S.J. and Bowen, B.J., 2019. Comparative dietary analysis of the black-flanked rock-wallaby (Petrogale lateralis lateralis), the euro (Macropus robustus erubescens) and the feral goat (Capra hircus) from Cape Range National Park, Western Australia. Australian Mammalogy, 41(2), pp.220-230.')
   
    def test_import_pa_post(self):                   
        with open("/src/app/tests/imports/assets/pa_true_test.tsv") as fp:
            response = self.client.post('/import/proximate_analysis', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)

    def test_import_pa_post_incorrect_file(self):       
        with open("/src/app/tests/imports/assets/pa_false_test.tsv") as fp:
            response = self.client.post('/import/proximate_analysis', {'name': 'fred', 'csv_file': fp})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Unable to upload file. Exception('Author not found')")
        self.assertEqual(response.status_code, 302)
    pass