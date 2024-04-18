from django.test import TestCase
from mb.utils.master_location_tools import *

class MasterLocationFilterTest(TestCase):
    def create_test_models():
        mlv1 = MasterLocationView(name="Suomi, Helsinki", reference="Kirja abc", master_habitat="Habitat_01")
        mlv2 = MasterLocationView(name="Suomi, Oulu", reference="Lehti 123", master_habitat="Habitat_02")
        mlv3 = MasterLocationView(name="Suomi, Joensuu", reference="Kirja abc", master_habitat="Habitat_02")
        mlv4 = MasterLocationView(name="USA, New York", reference="Aapinen abc", master_habitat="Habitat_03")
        mlv5 = MasterLocationView(name="USA, San Francisco", reference="Artikkeli abc", master_habitat="Habitat_03")

        objects = [mlv1, mlv2, mlv3, mlv4, mlv5]

        return objects
    def test_filter_case_1():
        
        pass
    def test_filter_case_2():
        pass
    def test_filter_case_3():
        pass
    def test_filter_case_4():
        pass
    def test_filter_case_5():
        pass