from django.test import TestCase
from unittest import skip
import pandas as pd
from imports.validation_lib.occurrence_validation import Occurrence_validation
from imports.validation_lib.base_validation import Validation
from mb.models import ChoiceValue

class ValidationTest(TestCase):


    def setUp(self):
        # Initialize your class or any other setup required
        self.instance = Validation()
        self.error_templates = self.instance.get_error_message_templates()

    def test_choicevalue(self):
        choicevalue_error = self.error_templates['gender'] % 'sex'

        # Test case 1: Gender is Male
        gender, created = ChoiceValue.objects.get_or_create(choice_set="Gender", caption="Male")

        if created == False:
            raise("Exception in creating MOC data (ChoiceValue: Gender and Male)")
        
        data = {"sex": "male"}  
        errors = self.instance.validate_choice_value(data, "sex", "choiceValue:gender")
        self.assertEqual(errors, [])

        # Test case 2: Gender is polkuauto        
        data = {"sex": "polkuauto"}  
        errors = self.instance.validate_choice_value(data, "sex", "choiceValue:gender")
        self.assertEqual(errors, [choicevalue_error])



    def test_boolean_validation(self):
        boolean_error = self.error_templates['boolean'] % 'boolean'

        # Test case 1: 'True' value
        data = {"boolean": True}  
        errors = self.instance.validate_boolean_fields(data, "boolean")
        self.assertEqual(errors, []) 

        # Test case 2: 'False' value
        data = {"boolean": False}  
        errors = self.instance.validate_boolean_fields(data, "boolean")
        self.assertEqual(errors, []) 

        # Test case 3: Invalid value
        data = {"boolean": "invalid"}  
        errors = self.instance.validate_boolean_fields(data, "boolean")
        self.assertEqual(errors, [boolean_error]) 

    def test_validate_author_fields(self):
        # Test case 1: Missing author field
        required_error = self.error_templates['required'] % 'author'
        author_error = self.error_templates['author'] % 'author'

        data = {}  # Empty dictionary
        errors = self.instance.validate_author_fields(data, 'author')
        self.assertEqual(errors, [required_error])

        # Test case 2: Invalid author format
        data = {'author': '1234-5678-9012-345'}  # Invalid format
        errors = self.instance.validate_author_fields(data, 'author')
        self.assertEqual(errors, [author_error])

        # Test case 3: Valid author format
        data = {'author': '1234-5678-9012-3456'}  # Valid format
        errors = self.instance.validate_author_fields(data, 'author')
        self.assertEqual(errors, [])

        # Test case 4: Valid author format with non-numeric characters
        data = {'author': 'abcd-efgh-ijkl-mnop'}  # Valid format with non-numeric characters
        errors = self.instance.validate_author_fields(data, 'author')
        self.assertEqual(errors, [author_error])

        # Test case 5: Valid author format with correct length but missing '-'
        data = {'author': '1234567890123456789'}  # Missing '-'
        errors = self.instance.validate_author_fields(data, 'author')
        self.assertEqual(errors, [author_error])

    def test_required_validation(self):
        required_error = self.error_templates['required'] % 'required'

        data = {"author": "some_value"}  
        errors = self.instance.validate_required_fields(data, 'required')
        self.assertEqual(errors, [required_error])  

        data = {"author": ""}  # Field is empty
        errors = self.instance.validate_required_fields(data, 'required')
        self.assertEqual(errors, [required_error])

    def test_in_fields(self):
        required_error = self.error_templates['in'] % 'in'
        # Test case 1, found in list
        data = {"in": "Species"}
        rule = "in:Subspecies,Varietas,Forma,Species,Genus,Nothogenus,Nothospecies,Nothosubspecies,Family,nan"
        error = self.instance.validate_in_fields(data, "in", rule)
        self.assertEqual(error, [])

        # Test case 2, not in list
        data = {"in": "cies"}
        rule = "in:Subspecies,Varietas,Forma,Species,Genus,Nothogenus,Nothospecies,Nothosubspecies,Family,nan"
        error = self.instance.validate_in_fields(data, "in", rule)
        self.assertEqual(error, [required_error])
    
    def test_alpha(self):
        required_error = self.error_templates["alpha"] % 'alpha'

        # Test case 1: not alphabets only
        data = {"alpha": "abc123"}
        error =self.instance.validate_alpha_fields(data, "alpha")
        self.assertEqual(error, [required_error])

        # Test case 2: valid
        data = {"alpha": "abcDEF"}
        error =self.instance.validate_alpha_fields(data, "alpha")
        self.assertEqual(error, [])

    def test_digits(self):
        required_error = self.error_templates["digits"] % 'digits'

        # Test case 1: not digits only
        data = {"digits": "abcDEF"}
        error =self.instance.validate_digit_fields(data, "digits")
        self.assertEqual(error, [required_error])

        # Test case 2: valid
        data = {"digits": "123456"}
        error =self.instance.validate_digit_fields(data, "digits")
        self.assertEqual(error, [])

    @skip # Alias database does not fill choice value db, makin every subtest fail
    def test_choice_value(self):
        gender, created = ChoiceValue.objects.get_or_create(choice_set="Gender", caption="Male")
        lifestage, created = ChoiceValue.objects.get_or_create(choice_set="Lifestage", caption="Adult")
        if gender != True and lifestage != True:
            return 
        # Test case 1: Valid choice value lifestage
        data = {"lifestage": "adult"}
        rule = "choiceValue:lifestage"
        error =self.instance.validate_choice_value(data, "lifestage", rule)
        self.assertEqual(error, [])

        # Test case 2: Valid choice value gender
        data = {"gender": "female"}
        rule = "choiceValue:gender"
        error =self.instance.validate_choice_value(data, "gender", rule)
        self.assertEqual(error, [])

        # Test case 3: invalid choice value for gender
        required_error = self.error_templates["gender"] % "gender"
        data = {"gender": "other"}
        rule = "choiceValue:gender"
        error =self.instance.validate_choice_value(data, "gender", rule)
        self.assertEqual(error, [required_error])
    
        
    def test_coordinate_format(self):
        test_dict = self.instance.coords_dict

        # Test cases for coordinate_format
        latitude = "12.3456"
        longitude = "-78.9012"
        coords = f"{latitude}, {longitude}" 
        self.assertEqual(self.instance.coordinate_format(coords, test_dict), "decimal degrees")

        latitude = "12°34.567'N"
        longitude = "78°90.123'W"
        coords = f"{latitude}, {longitude}" 
        self.assertEqual(self.instance.coordinate_format(coords, test_dict), "degrees minutes")

        latitude = "12°34'56.789\" N"
        longitude = "78°90'12.345\" W"
        coords = f"{latitude}, {longitude}" 
        self.assertEqual(self.instance.coordinate_format(coords, test_dict), "degrees decimals")
        self.assertEqual(self.instance.coordinate_format("32S 485146mE 4037735mN", test_dict), "UTM")
        self.assertEqual(self.instance.coordinate_format("Invalid Coordinate", test_dict), "No match found")


    def test_validate_coordinateSystem_fields(self):
        coord_error = self.error_templates['verbatimCoordinateSystem'] % 'verbatimCoordinateSystem'
        rule = "coordinateSystem:VerbatimLatitude,VerbatimLongitude,VerbatimCoordinates"
        # Mock data for testing
        mock_data = {
            "verbatimCoordinateSystem": "decimal degrees",
            "verbatimLatitude": "40.7128",
            "verbatimLongitude": "-74.0060",
            "verbatimCoordinates": "32S 485146mE 4037735mN"
        }
        mock_data2 = {
            "verbatimCoordinateSystem": "decimal degrees",
            "verbatimLatitude": "40.7128",
            "verbatimLongitude": "-74.0060",
            "verbatimCoordinates": "nan"
        }

        mock_data3 = {
            "verbatimCoordinateSystem": "decimal degrees",
            "verbatimLatitude": "40.7128",
            "verbatimLongitude": "nan",
            "verbatimCoordinates": "nan"
        }
        # Test cases for validate_coordinateSystem_fields
        self.assertNotEqual(self.instance.validate_coordinateSystem_fields(mock_data, "verbatimCoordinateSystem",rule), [])
        self.assertEqual(self.instance.validate_coordinateSystem_fields(mock_data2, "verbatimCoordinateSystem",rule), [])
        self.assertEqual(self.instance.validate_coordinateSystem_fields(mock_data3, "verbatimCoordinateSystem", rule), [coord_error])
        self.assertNotEqual(self.instance.validate_coordinateSystem_fields(mock_data3, "verbatimCoordinateSystem",rule ), []) 


    def test_min(self):
        required_error = self.error_templates['min'] % 'min'

        # Test case 1: too small min value
        data = {"min": 10}
        rule = "min:20"
        error =self.instance.validate_min_fields(data, "min", rule)
        self.assertEqual(error, [required_error])

        # Test case 2: too short min value
        data = {"min": "pekka"}
        rule = "min:20"
        error =self.instance.validate_min_fields(data, "min", rule)
        self.assertEqual(error, [required_error])

        # Test case 3: correct value min value
        data = {"min": 1337}
        rule = "min:20"
        error =self.instance.validate_min_fields(data, "min", rule)
        self.assertEqual(error, [])

        # Test case 4: correct length min value
        data = {"min": "Saippuakauppias"}
        rule = "min:10"
        error =self.instance.validate_min_fields(data, "min", rule)
        self.assertEqual(error, [])

    def test_max(self):
        required_error = self.error_templates['max'] % 'max'

        # Test case 1: too large max value
        data = {"max": 30}
        rule = "max:20"
        error =self.instance.validate_max_fields(data, "max", rule)
        self.assertEqual(error, [required_error])

        # Test case 2: too long max value
        data = {"max": "Saippuakauppias"}
        rule = "max:10"
        error =self.instance.validate_max_fields(data, "max", rule)
        self.assertEqual(error, [required_error])

        # Test case 3: correct value min value
        data = {"max": 1337}
        rule = "max:2000"
        error =self.instance.validate_max_fields(data, "max", rule)
        self.assertEqual(error, [])

        # Test case 4: correct length min value
        data = {"max": "saippuakauppias"}
        rule = "max:30"
        error =self.instance.validate_max_fields(data, "max", rule)
        self.assertEqual(error, [])

    def test_regex(self):
            required_error = self.error_templates['regex'] % 'regex'
            # Test case 1: valid regex
            data = {"regex": "abcdef1001"} 
            rules = "regex:.*([1-2][0-9]{3})"
            errors = self.instance.validate_regex_fields(data,"regex", rules)
            self.assertEqual(errors, [])

            # Test case 2:
            data = {"regex": "abcdef"} 
            rules = "regex:.*([1-2][0-9]{3})"
            errors = self.instance.validate_regex_fields(data,"regex", rules)
            self.assertEqual(errors, [required_error])

            # Test case 3:
            data = {"regex": "Original study"} 
            rules = "regex:.*([1-2][0-9]{3})|(Original study)'"
            errors = self.instance.validate_regex_fields(data,"regex", rules)
            self.assertEqual(errors, [required_error])