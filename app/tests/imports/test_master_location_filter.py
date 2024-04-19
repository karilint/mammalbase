from django.test import TestCase
from mb.utils.master_location_tools import filter

class MasterLocationView():
        def __init__(self, name, reference, master_habitat):
            self.name = name
            self.reference = reference
            self.master_habitat = master_habitat

class MasterLocationFilterTest(TestCase):
    
    def setUp(self):
        pass
    
    def create_test_models(self):
        mlv1 = MasterLocationView(name="Suomi, Helsinki", reference="Kirja abc", master_habitat="Habitat_01")
        mlv2 = MasterLocationView(name="Suomi, Oulu", reference="Lehti 123", master_habitat="Habitat_02")
        mlv3 = MasterLocationView(name="Suomi, Joensuu", reference="Kirja abc", master_habitat="Habitat_02")
        mlv4 = MasterLocationView(name="USA, New York", reference="Aapinen abc", master_habitat="Habitat_03")
        mlv5 = MasterLocationView(name="USA, San Francisco", reference="Artikkeli abc", master_habitat="Habitat_03")

        objects = [mlv1, mlv2, mlv3, mlv4, mlv5]


        return objects
    def test_filter_case_1(self):
        objs = self.create_test_models()

        dic = {"master_location" : "Suomi"}

        filtered_objs = filter(objs, dic)

        self.assertEqual(len(filtered_objs), 3)
    
    def test_filter_case_2(self):
        objs = self.create_test_models()

        dic = {"master_location" : "Suomi", "reference" : "Kirja abc"}

        filtered_objs = filter(objs, dic)

        self.assertEqual(len(filtered_objs), 2)
    
    def test_filter_case_3(self):
        objs = self.create_test_models()

        dic = {"master_location" : "New York", "master_habitat" : "nan"}

        filtered_objs = filter(objs, dic)

        self.assertEqual(len(filtered_objs), 0)
    
    def test_filter_case_4(self):
        objs = self.create_test_models()

        dic = {"master_habitat" : "Habitat"}

        filtered_objs = filter(objs, dic)

        self.assertEqual(len(filtered_objs), 5)
    
    def test_filter_case_5(self):
        objs = self.create_test_models()

        dic = {"master_location" : "", "reference" : "", "master_habitat" : ""}

        filtered_objs = filter(objs, dic)

        self.assertEqual(len(filtered_objs), 5)

    def test_filter_case_6(self):
        objs = self.create_test_models()

        dic = {"master_location" : ", ", "reference" : " ", "master_habitat" : "_"}

        filtered_objs = filter(objs, dic)

        self.assertEqual(len(filtered_objs), 5)
