"""
The MIT License (MIT)

Copyright (c) 2016 Sadaf Waziry sadaf1.waziry@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import re, datetime, sys
from mb.models.models import ChoiceValue, SourceReference
from django.apps import apps


class Validation():

    def __init__(self):
        """
        Validation class. The class is derived from https://github.com/walid-mashal/laravel-validation
        """
        self.error_message_templates = self.get_error_message_templates()
        self.custom_error_messages = {}
        # List to store the error messages in
        self.errors = []

    def validate(self, data, rules, custom_messages=None):
        """Validate the 'data' according to the 'rules' given, returns a list of errors named 'errors'"""

        if custom_messages:
            self.custom_error_messages = custom_messages
        
        #iterate through the rules dictionary, fetching each rule name (dictionary key) one by one
        for field_name in rules:

            #fetch the rule (value of dictionary element) from "rules" dictionary for the current rule name (dictionary key) and split it to get a list
            field_rules = rules[field_name].split('|')
            
            #field_errors will keep the errors for a particular field, which will be appended to the main "errors" list
            field_errors = []

            #now looping through rules of one field one rule at a time with each iteration
            for rule in field_rules:
                field_errors.extend(self.validate_field_rule(data, field_name, rule, field_rules))

            self.errors.extend(field_errors)

        return self.errors

    def validate_field_rule(self, data, field_name, rule, field_rules=None):
        """Validates the data of the field based on the rule assigned"""

        rule_error = ""

        if rule == "boolean":
            rule_error = self.validate_boolean_fields(data, field_name)

        elif rule == "date":
            rule_error = self.validate_date_fields(data, field_name, field_rules)
        
        elif rule == "author":
            rule_error = self.validate_author_fields(data, field_name)

        elif rule == "required":
            rule_error = self.validate_required_fields(data, field_name)
        
        elif rule == "verbatimScientificName":
            rule_error = self.validate_verbatim_scientific_name(data, field_name, field_rules)

        elif rule == "verbatimLatitude":
            rule_error = self.validate_verbatim_latitude(data, field_name)

        elif rule == "verbatimLongitude":
            rule_error = self.validate_verbatim_longitude(data, field_name)

        elif rule == "verbatimEventDate":
            rule_error = self.validate_verbatim_eventdate(data, field_name)
        
        elif rule == "gender":
            rule_error = self.validate_gender(data, field_name, field_rules)

        elif rule == "lifeStage":
            rule_error = self.validate_life_stage(data, field_name, field_rules)
        
        elif rule.startswith("in"):
            rule_error = self.validate_in_fields(data,field_name, rule)
        
        elif rule == "sequence":
            rule_error = self.validate_sequence_fields(data, field_name, field_rules)
        
        elif rule == "measurementValue":
            rule_error = self.validate_measurement_value(data, field_name, field_rules)
        
        elif rule == "alpha":
            rule_error = self.validate_alpha_fields(data,field_name)

        elif rule.startswith("in_db"):
            rule_error = self.validate_in_db(data, field_name, field_rules)
            
        elif rule == "digits":
            rule_error = self.validate_digit_fields(data,field_name)

        elif rule.startswith("max"):
            rule_error = self.validate_max_fields(data,field_name,rule)

        elif rule.startswith("min"):
            rule_error = self.validate_min_fields(data,field_name,rule)
        
        elif rule.startswith("nameYear"):
            rule_error = self.validate_nameYear_fields(data,field_name)
        
        elif rule.startswith("regex"):
            rule_error = self.validate_regex_fields(data,field_name, rule)

        elif rule.startswith("verbatimCoordinates"):
            rule_error = self.validate_verbatim_coordinates(data, field_name)

        
        # Add more elif blocks for each additional rule you want to handle
        
        return rule_error
    
    def validate_verbatim_coordinates(self, data, field_name):
        """Validate verbatimCoordinates

        Args:
            data (python-dictionary): Generaged dictionary from tsv-file.
            field_name (str): field name

        Returns:
            list: Possible validation errors in list. Otherwise empty list if valdion is correct.
        """
        errs = []

        #before matching remove all whitespaces from str(data[field_name])

        return errs
    
    def validate_verbatim_eventdate(self, data, field_name):
        """Validate verbatimEventDate

        Args:
            data (python-dictionary): Generaged dictionary from tsv-file.
            field_name (str): field name

        Returns:
            list: Possible validation errors in list. Otherwise empty list if valdion is correct.
        """
        return []
    def validate_verbatim_latitude(self, data, field_name):
        return []
    
    def validate_verbatim_longitude(self, data, field_name):
        return []

    def validate_boolean_fields(self, data, field_name):
        """Validate boolean values.

        Args:
            data (python-dictionary): Generaged dictionary from tsv-file.
            field_name (str): field name

        Returns:
            list: Possible validation errors in list. Otherwise empty list if valdion is correct.
        """
        errs = []
        try:
            if data[field_name] != (True or False):
                errs.append(self.return_field_message(field_name,"boolean"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name,'boolean'))

        return errs  

    def validate_digit_fields(self, data, field_name):
        """Used for validating integer fields, returns a list of error messages"""
        errs = []

        try:
            if not isinstance(float(data[field_name]),(int, float)) or data[field_name] == "nan":
                errs.append(self.return_field_message(field_name,"digits"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name,'digits'))
        return errs
    
    def validate_nameYear_fields(self, data, field_name):
        """Validate nameYear

        Args:
            data (python-dictionary): Generaged dictionary from tsv-file.
            field_name (str): field name

        Returns:
            list: Possible validation errors in list. Otherwise empty list if validation is correct.
        """

        errs = []
        try:
            name_year_pattern = r"\((?:\w+(?:,\s*\d{1,4})?|\w+)\)(?:\s*|$)|\w+,\s*\d{1,4}"
            if not re.match(name_year_pattern, data[field_name]) or data[field_name].count('(') != data[field_name].count(')'):
                errs.append(self.return_field_message(field_name, "invalid name and year format"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, 'integer'))
        return errs

    def validate_date(self, data, field_name):
        """Validate date

        Args:
            data (python-dictionary): Generaged dictionary from tsv-file.
            field_name (str): field name

        Returns:
            list: Possible validation errors in list. Otherwise empty list if validaion is correct.
        """
        errs = []
        try:
            date_str = data[field_name]
            # Attempt to parse the date using known formats
            try:
                datetime.datetime.strptime(date_str, "%d.%m.%Y")  # European style: dd.mm.yyyy
            except ValueError:
                try:
                    datetime.datetime.strptime(date_str, "%m.%d.%Y")  # US style: mm.dd.yyyy
                except ValueError:
                    try:
                        datetime.datetime.strptime(date_str, "%B %Y")  # Month Year format
                    except ValueError:
                        try:
                            datetime.datetime.strptime(date_str, "%Y")  # Year only format
                        except ValueError:
                            try:
                                datetime.datetime.strptime(date_str, "%B")  # Month only format
                            except ValueError:
                                errs.append(self.return_field_message(field_name, "invalid date format"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, 'required'))

        return errs 
    
    def validate_alpha_fields(self, data, field_name):
        """Used for validating fields for alphabets only, returns a list of error messages"""
        errs = []

        try:
            if not re.match("^[a-zA-Z\s]+$",str(data[field_name])) and str(data[field_name]) != "nan":
                errs.append(self.return_field_message(field_name,"alpha"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name,'alpha'))
        
        return errs

    def validate_in_fields(self, data, field_name, rule):
        """Used for validating fields for some number of values to allow, returns a list of error messages"""
        #retrieve the value for that in rule
        ls = rule.split(':')[1].split(',')
        errs = []

        try:
            if str(data[field_name]) not in ls:
                errs.append(self.return_field_message(field_name, "in"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name,'in'))
        return errs

    def validate_author_fields(self, data, field_name):
        """Validate author.

        Args:
            data (python-dictionary): Generaged dictionary from tsv-file.
            field_name (str): field name

        Returns:
            list: Possible validation errors in list. Otherwise empty list if validaion is correct.
        """
        errs = []
        try:
            author = data[field_name]
            if not author:
                errs.append(self.return_field_message(field_name, "required"))
            elif len(author) != 19 or author[4] != '-' or author[9] != '-' or author[14] != '-':
                errs.append(self.return_field_message(field_name, "invalid author format"))
            else:
                parts = author.split('-')
                if len(parts) != 4 or not all(part.isdigit() and len(part) == 4 for part in parts):
                    errs.append(self.return_field_message(field_name, "invalid author format"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, 'required'))

        return errs


    def validate_required_fields(self, data, field_name):
        """Used for validating required fields, returns a list of error messages"""
        errs = []
        try:
            if str(data[field_name]) == "" or str(data[field_name]) == "nan":
                errs.append(self.return_field_message(field_name,"required"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name,'required'))

        return errs     

    def validate_verbatim_scientific_name(self, data, field_name, field_rules):
        """Validate verbatim scientific name field"""
        # Your validation logic here
        # Example:


        if not data.get(field_name):
            return self.return_no_field_message(field_name, 'verbatim scientific name')
        # Additional validation logic...
        return ""  # No error message if validation passes


    def validate_gender(self, data, field_name, field_rules):
        """Validate gender field"""
        gender = str(data[field_name])

        # Change the first letter to uppercase
        choicevalue = ChoiceValue.objects.filter(choice_set="Gender", caption=gender.capitalize())

        if gender == 'nan':
            return ""
        if len(choicevalue) == 0:
            return self.return_no_field_message(field_name, 'sex')
        if gender.capitalize() == str(choicevalue[0].caption):
            return ""
        else:
            return self.return_no_field_message(field_name, 'sex')

    def validate_life_stage(self, data, field_name, field_rules):
        """Validate life stage"""
        life_stage = str(data[field_name])
        print("lifestage checker: " + life_stage)

        # Change the first letter to uppercase
        choicevalue = ChoiceValue.objects.filter(choice_set="Lifestage", caption=life_stage.capitalize())

        if  life_stage == str(data[field_name]) == 'nan':
            return ""
        if len(life_stage) == 0:
            return self.return_no_field_message(field_name, 'lifestage')
        if life_stage.capitalize() == str(choicevalue[0].caption):
            return ""
        else:
            return self.return_no_field_message(field_name, 'lifestage')

    def validate_measurement_value(self, data, field_name, field_rules):
        """Validate measurement value field"""
        if not data.get(field_name):
            return self.return_no_field_message(field_name, 'measurement value')
        measurement_value = data[field_name]
        try:
            measurement_value = int(measurement_value)
            if measurement_value < 1:
                return self.return_field_message(field_name, "measurement value must be non-negative or 0")
        except ValueError:
            return self.return_field_message(field_name, "measurement value must be an integer")

        return ""

    def validate_in_db(self, data, field_name, field_rules):
        """Validate in db.

        Args:
            data (python-dictionary): Generaged dictionary from tsv-file.
            field_name (str): field name

        Returns:
            list: Possible validation errors in list. Otherwise empty list if validaion is correct.
        """
        model = apps.get_model('mb', field_rules[0])
        errs = []

        if not model.objects.filter(**{field_rules[1]: data[field_name]}).exists():
            errs.append(self.return_no_field_message(field_name,'in_db'))
        return errs


    def validate_regex_fields(self, data, field_name, rule):
        """Used for validating field data to match a regular expression, returns a list of error messages"""

        regex = str(rule.split(':')[1])
        errs,result = self.match_regular_expression(regex,str(data[field_name]),"regex")

        #in case the RE did not match or there was a key error
        if not result:
            errs.append(self.return_field_message(field_name,"regex"))
        return errs

    def validate_lengths_fields(self, data, field_name, field_rules):
        """Validate lengths field"""

        # Retrieve the specific value for that rule
        specific_value = field_rules.split(':')[1]
        errs = []
        try:
            if data[field_name] != specific_value:
                errs.append(self.return_field_message(field_name, "specific", specific_value))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, 'specific'))

        return errs

    def validate_max_fields(self, data, field_name, rule):
        """Used for validating fields for a maximum integer value, returns a list of error messages"""

        #retrieve the value for that max rule
        max_value = int(rule.split(':')[1])

        errs = []
        try:
            if isinstance(data[field_name],(float,int)):
                if (data[field_name]) > max_value:
                    errs.append(self.return_field_message(field_name,"max"))
            else:
                if len(str(data[field_name])) > max_value:
                    errs.append(self.return_field_message(field_name,"max"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name,'maximum'))

        return errs

    def validate_min_fields(self, data, field_name, rule):
        """Used for validating fields for a minimum integer value, returns a list of error messages"""

        #retrieve the value for that min rule
        min_value = int(rule.split(':')[1])
        errs = []
        try:
            if isinstance(data[field_name],(float,int)):
                if (data[field_name]) < min_value:
                    errs.append(self.return_field_message(field_name,"min"))
            else:
                if len(str(data[field_name])) < min_value:
                    errs.append(self.return_field_message(field_name,"min"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name,'minimum'))

        return errs

    # Add more validation functions for other fields

    def retrieve_date_format(self,field_rules):
        #loop through each rule for the particular field to check if there is any date_format rule assigned
        for rule in field_rules:
            #if there is a date_format rule assigned then fetch the date format from that
            if rule.startswith("date_format"):
                date_format = rule.split(":")[1]
                
                return date_format

        #if no date_format found, return the default date format
        return '%m/%d/%Y'

    def match_regular_expression(self,regex,field_value,rule_name):
        comp_re = re.compile(regex, re.IGNORECASE)
        errs = []

        try:
            result = comp_re.match(field_value)
        except KeyError:
            errs.append(self.return_no_field_message(field_value,rule_name))
            result = "error"

        return errs,result

    def return_no_field_message(self, field_name, rule_name):
        """Return no field message.

        Args:
            data (python-dictionary): Generaged dictionary from tsv-file.
            field_name (str): field name

        Returns:
            str: Error message from dictionary (see custom_error_messages-function).
        """
        if self.custom_error_messages.__contains__(field_name+".no_field"):
            return self.custom_error_messages[field_name+".no_field"]
        else:
            return self.error_message_templates['no_field'] % (field_name,rule_name)

    def return_field_message(self, field_name, rule_name):
        """Return field message.

        Args:
            data (python-dictionary): Generaged dictionary from tsv-file.
            field_name (str): field name

        Returns:
            str: Error message from dictionary (see custom_error_messages-function).
        """
        if self.custom_error_messages.__contains__(field_name+"."+rule_name):
            return self.custom_error_messages[field_name+"."+rule_name]
        else:
            return self.error_message_templates[rule_name] % (field_name)

    def is_valid(self, data, rules):
        """Validates the data according to the rules, returns True if the data is valid, and False if the data is invalid"""

        errors = self.validate(data,rules)

        self.errors = errors

        return not len(errors) > 0

    def get_error_message_templates(self):
        """Dictionary for error messages.

        Returns:
            dictionary: list of all possible error messages.
        """
        return {
            "after": "'%s' is an invalid after date",
            "alpha":"'%s' can have only alphabets",
            "alpha_num":"'%s' can have only alphabets or numbers",        
            "before":"'%s' is an invalid before date ",
            "between":"'%s' has an invalid value for between field",
            "boolean":"'%s' has invalid value for boolean field",
            "confirmed":"'%s' must have a pair field",
            "date":"'%s' value does not match date format",
            "digits":"'%s' must be an integer",
            "different":"'%s' has invalid value for same rule ",
            "email":"'%s' must be a valid email address",
            "in":"'%s' has invalid value for in rule",
            "ip":"'%s' must be a valid IP address",
            "max":"The maximum value for the field '%s' is invalid",
            "min":"The minimum value for the field '%s' is invalid",
            "not_in":"'%s' has invalid value for not_in rule",
            "present":"The data dictionary must have a nullable field name '%s'",
            "phone":"'%s' must be a valid Phone Number",
            "regex":"'%s' field does not match the RE ",
            "required":"'%s' must be filled",
            "same":"'%s' has invalid value for same rule",
            "size":"'%s' has invalid value for size rule",
            "website":"'%s' must be a valid Website URL",
            "no_field":"No field named '%s' to validate for %s rule",
            "sex": "%s has invalid value",
            "lifestage": "%s has invalid value"
        }
    
    def get_custom_error_messages(self):
        """Dictionary for custom error messages.

        Returns:
            dictionary: list of all possible error messages.
        """
        return {
            "_comment": "You did not provide any field named <feld_name> in your data dictionary",
            "field_name.rule":"You did not provide any field named field_name in your data dictionary",
            "month_day.regex":"You did not provide any field named month_day in your data dictionary",
            "phone.max":"You did not provide any field named phone in your data dictionary",
            "month_day.required":"You did not provide any field named month_day in your data dictionary",
            "new_password_confirmation.same":"You did not provide any field named %s in your data dictionary",
            "phone.no_field":"You did not provide any field named phone in your data dictionary",
            "birthday.date_format":"You did not provide any field named birthday in your data dictionary",
            "new_password.alpha":"field new_password can only have alphabet values",
            "host.no_field":"You did not provide any field named host in your data dictionary",
            "email.no_field":"You did not provide any field named email in your data dictionary",
            "nationality.no_field":"You did not provide any field named nationality in your data dictionary",
            "active.no_field":"You did not provide any field named active in your data dictionary",
            "age.no_field":"You did not provide any field named age in your data dictionary"
        }