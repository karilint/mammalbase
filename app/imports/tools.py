import re
import json
import sys
import traceback
from datetime import timedelta
from decimal import Decimal

import requests

import pandas as pd
import numpy

from django.contrib import messages
from django.db import transaction
from django.db import DatabaseError
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from requests_cache import CachedSession

from mb.models import ChoiceValue, DietSet, EntityClass, MasterReference, SourceAttribute, SourceChoiceSetOptionValue
from mb.models import SourceChoiceSetOption, SourceEntity, SourceLocation, SourceMeasurementValue, SourceMethod
from mb.models import SourceReference, SourceStatistic, SourceUnit, TimePeriod, DietSetItem, FoodItem ,EntityRelation
from mb.models import MasterEntity, ProximateAnalysisItem, ProximateAnalysis
from itis.models import TaxonomicUnits, Kingdom, TaxonUnitTypes
import itis.views as itis
from config.settings import ITIS_CACHE


class Check:
    def __init__(self, request):
        self.request = request
        self.id = None

    def check_all_ds(self, df, force=False):
        return (
            self.check_headers_ds(df) and 
            self.check_author(df) and 
            self.check_verbatimScientificName(df) and
            self.check_taxonRank(df) and
            self.check_gender(df) and
            self.check_verbatim_associated_taxa(df) and
            self.check_sequence(df) and
            self.check_measurementValue(df) and 
            self.check_part(df) and 
            self.check_references(df, force) and
            self.check_lengths(df)
        )
    
    def check_all_ets(self, df):
        return (
            self.check_headers_ets(df) and
            self.check_author(df) and
            self.check_verbatimScientificName(df) and
            self.check_taxonRank(df) and
            self.check_lengths(df) and
            self.check_min_max(df)
        )
    
    def check_all_pa(self, df, force=False):
        return (
            self.check_headers_pa(df) and
            self.check_author(df) and
            self.check_verbatimScientificName(df, False) and
            self.check_lengths(df) and
            self.check_part(df) and
            self.check_references(df, force) and
            self.check_nfe(df) and
            self.check_cf_valid(df) and
            self.check_measurementValue(df)
        )

    def check_valid_author(self, df):
        counter = 1
        for author in (df.loc[:, 'author']):
            counter += 1
            if author == "nan":
                messages.error(self.request, "The author is empty at row " +  str(counter) + ".")
                return False
            data = SocialAccount.objects.all().filter(uid=author)
            if not data.exists():
                self.id = None
                messages.error(self.request, "The author " + str(author) + " is not a valid ORCID ID at row " +  str(counter) + ".")
                return False
            self.id = data[0].user_id
        return True

    def check_headers_ds(self, df):
        import_headers = list(df.columns.values)
        accepted_headers = ['author', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence',  'references']

        for header in accepted_headers:
            if header not in import_headers:
                messages.error(self.request, "The import file does not contain the required headers. The missing header is: " + str(header) + ".")
                return False
        return True
    
    def check_headers_ets(self, df):
        import_headers = list(df.columns.values)
        accepted_headers = ['references', 'verbatimScientificName', 'taxonRank', 'verbatimTraitName', 'verbatimTraitUnit', 'author']

        for header in accepted_headers:
            if header not in import_headers:
                messages.error(self.request, "The import file does not contain the required headers. The missing header is: " + str(header) + ".")
                return False
        return True
    
    def check_headers_pa(self, df):
        import_headers = list(df.columns.values)
        required_headers = [
            'verbatimScientificName',
            'PartOfOrganism',
            'author',
            'references'
            ]
        optional_headers = {
            "individualCount":float,
            "measurementMethod":str,
            "measurementDeterminedBy":str,
            "verbatimLocality":str,
            "measurementRemarks":str,
            "verbatimEventDate":str,
            "verbatimTraitValue__moisture":float,
            "dispersion__moisture":float,
            "measurementMethod__moisture":str,
            "verbatimTraitValue__dry_matter":float,
            "dispersion__dry_matter":float,
            "measurementMethod__dry_matter":str,
            "verbatimTraitValue__ether_extract":float,
            "dispersion__ether_extract":float,
            "measurementMethod__ether_extract":str,
            "verbatimTraitValue__crude_protein":float,
            "dispersion__crude_protein":float,
            "measurementMethod__crude_protein":str,
            "verbatimTraitValue__crude_fibre":float,
            "dispersion__crude_fibre":float,
            "measurementMethod__crude_fibre":str,
            "verbatimTraitValue_ash":float,
            "dispersion__ash":float,
            "measurementMethod_ash":str,
            "verbatimTraitValue__nitrogen_free_extract":float,
            "dispersion__nitrogen_free_extract":float,
            "measurementMethod__nitrogen_free_extract":str,
            "associatedReferences":str
        }
        type_names = {
            int:"a number",
            float:"a number or decimal value",
            str:"text"
        }

        for header in required_headers:
            if header not in import_headers:
                messages.error(self.request, f"The import file does not contain the required headers. The missing header is: {str(header)}.")
                return False
        
        for header in import_headers:
            if header in optional_headers:
                for row, value in enumerate(df.loc[:, header]):
                    if optional_headers[header]!=str:
                        if isinstance(value, str):
                            value = value.replace(",",".")
                        try:
                            df.loc[row, header] = optional_headers[header](value)
                        except ValueError:
                            messages.error(self.request, f"The {header} on row {row+1} is an incorrect type. It should be {type_names[optional_headers[header]]}.")
                            return False
        return True

    def _calculate_nfe(self, row):
        value_sum = sum([possible_nan_to_zero(row[value]) for value in row.keys() if ("verbatimTraitValue" in value and not "nitrogen_free_extract" in value)])
        return min(
            abs(value_sum-100),
            abs(value_sum-1000)
        )

    def check_nfe(self, df):
        missing_nfe_message = "\nNot reported: calculated by difference"
        headers = list(df.columns.values)
        if 'verbatimTraitValue__nitrogen_free_extract' in headers:
            mask = df["verbatimTraitValue__nitrogen_free_extract"].copy()
            mask[mask.notnull()]=""
            new_mm = df['measurementMethod__nitrogen_free_extract'].fillna(mask.fillna(missing_nfe_message))
            new_mm.replace(r'^$', numpy.nan, regex=True, inplace=True)
            df["measurementMethod__nitrogen_free_extract"] = new_mm
            df["verbatimTraitValue__nitrogen_free_extract"].fillna(df.apply(self._calculate_nfe, axis=1), inplace=True)
        else:
            df["measurementMethod__nitrogen_free_extract"] = missing_nfe_message
            df["verbatimTraitValue__nitrogen_free_extract"] = df.apply(self._calculate_nfe, axis=1)
            df["dispersion__nitrogen_free_extract"] = numpy.nan
        
        return True

    def _check_if_plant(self, name):
        rank_id = generate_rank_id(name)
        try:
            kingdom = rank_id[max(rank_id)]['data'][0]['results'][0]['classification_path'].split('-')[0]
        except ValueError: 
            return None
        return kingdom == "Plantae"
    
    def check_cf_valid(self, df):
        headers = list(df.columns.values)
        for row in range(df.shape[0]):
            is_plant = self._check_if_plant(df.loc[row, "verbatimScientificName"])
            if is_plant is None:
                continue
            if is_plant and ('verbatimTraitValue__crude_fibre' not in headers or possible_nan_to_zero(df.loc[row, 'verbatimTraitValue__crude_fibre'])==0):
                messages.error(self.request, f"Item of type plantae is missing required value verbatimTraitValue__crude_fibre on row {row}.")
                return False
        return True

    def check_author(self, df):
        for row, author in enumerate(df.loc[:, 'author'], 1):
            if len(str(author)) != 19:
                messages.error(self.request, f"The author \'{author}\' on row {row} is not in the correct form.")
                return False
            if "X" in author:
                author = author.replace("X", "")
            if "-" in author:
                author = author.replace("-", "")
            if not author.isdigit():
                messages.error(self.request, f"The author \'{author}\' on row {row} is not in the correct form.")
                return False
        return True

    def check_verbatimScientificName(self, df, taxon_rank_included=True):
        for row, name in enumerate(df.loc[:, 'verbatimScientificName'], 1):
            if name == "nan" or pd.isna(name):
                messages.error(self.request, f"Scientific name \'{name}\' is empty at row {row}.")
                return False
            if len(name) > 250:
                messages.error(self.request, f"Scientific name \'{name[:10]}...\' is too long at row {row}.")
                return False
        if not taxon_rank_included:
            return True
        df_new = df[['verbatimScientificName', 'taxonRank']]
        for row, item in enumerate(df_new.values, 1):
            names_list = item[0].split()

            if len(names_list) > 3 and not any(x in {"sp.", "sp", "cf.", "cf", "indet.", "indet", "aff.", "aff", "spp.", "spp"} for x in names_list):
                messages.error(self.request, f"Scientific name \'{str(item[0])}\' is not in the correct format on row {row}.")
                return False
            if len(names_list) == 3 and item[1] not in {'Subspecies', 'subspecies'} and not any(x in {"sp.", "sp", "cf.", "cf", "indet.", "indet", "aff.", "aff", "spp.", "spp"} for x in names_list):
                messages.error(self.request, f"Scientific name \'{str(item[0])}\' is not in the correct format or taxonomic rank \'{str(item[1])}\' should be 'Subspecies' on row {row}.")
                return False
            if len(names_list) == 2 and item[1] not in {'Species', 'species'} and not any(x in {"sp.", "sp", "cf.", "cf", "indet.", "indet", "aff.", "aff", "spp.", "spp"} for x in names_list):
                messages.error(self.request, f"Scientific name \'{str(item[0])}\' is not in the correct format or taxonomic rank \'{str(item[1])}\' should be 'Species' on row {row}.")
                return False
            if len(names_list) == 1 and item[1] not in {'Genus', 'genus'} and not any(x in {"sp.", "sp", "cf.", "cf", "indet.", "indet", "aff.", "aff", "spp.", "spp"} for x in names_list):
                messages.error(self.request, f"Scientific name \'{str(item[0])}\' is not in the correct format or taxonomic rank \'{str(item[1])}\' should be 'Genus' on row {row}.")
                return False
        return True

    def check_taxonRank(self, df):
        counter = 1
        for rank in (df.loc[:, 'taxonRank']):
            counter += 1
            if rank not in ['Genus', 'Species', 'Subspecies', 'genus', 'species', 'subspecies']:
                messages.error(self.request, "Taxonomic rank is not in the correct form on the line " + str(counter) + ".")
                return False
        return True
    
    def check_gender(self, df):
        headers = list(df.columns.values)
        if 'sex' not in headers:
            return True
        counter = 1
        for value in (df.loc[:, 'sex']):
            counter += 1
            if str(value).lower() != 'nan':
                try: 
                    if int(value) != 22 and int(value)!= 23:
                        messages.error(self.request, 'Gender is not in the correct format on the line '+str(counter)+' it should be 22 for male or 23 for female')
                        return False
                except ValueError:
                        messages.error(self.request, 'Gender is not in the correct format on the line '+str(counter)+' it should be 22 for male or 23 for female')
                        return False
        return True


    def check_verbatim_associated_taxa(self, df):
        counter = 1
        for item in (df.loc[:, 'verbatimAssociatedTaxa']):
            counter += 1
            if item == "nan" or pd.isna(item):
                messages.error(self.request, "The line " + str(counter) + " should not be empty on the column 'verbatimAssociatedTaxa'.")
                return False
            if len(item) > 250:
                messages.error(self.request, "verbatimAssociatedTaxa is too long at row " + str(counter) + ".")
                return False
        return True

    def check_sequence(self, df):
        import_headers = list(df.columns.values)
        has_measurementvalue =  "measurementValue" in import_headers
        if has_measurementvalue:
            df_new = df[['verbatimScientificName', 'verbatimAssociatedTaxa', 'sequence', 'references', 'measurementValue']]
        else:
            df_new = df[['verbatimScientificName', 'verbatimAssociatedTaxa', 'sequence', 'references']]
        optional_headers = [
            'verbatimLocality',
            'habitat',
            'samplingEffort',
            'sex',
            'individualCount',
            'verbatimEventDate',
            'measurementMethod',
            'associatedReferences'
        ]
        counter = 0
        total = 1
        fooditems = []
        compare = []

        for lines, item in enumerate(df_new.values,2):
            if str(item[2]).isnumeric():
                if int(item[2]) == counter:
                    if has_measurementvalue:
                        if item[4] > measurementvalue_reference:
                            messages.error(self.request, "Measurement value on the line " + str(lines) + " should not be larger than " + str(measurementvalue_reference) + ".")
                            return False
                    if has_measurementvalue:
                        measurementvalue_reference = item[4]
                    if item[0] != scientific_name:
                        messages.error(self.request, "Scientific name on the line " + str(lines) + " should be '" + str(scientific_name) + "'.")
                        return False
                    if item[3] != references:
                        messages.error(self.request, "References on the line " + str(lines) + " should be '" + str(references) + "'.")
                        return False
                    if item[1] in fooditems:
                        messages.error(self.request, "Food item on the line " + str(lines) + " is already mentioned for this diet set.")
                        return False
                    fooditems.append(item[1])
                    counter += 1
                    total += int(item[2])

                elif int(item[2]) == 1:
                    reference_list = [item[0], item[3]]
                    if has_measurementvalue:
                        measurementvalue_reference = item[4]

                    for header in optional_headers:
                        if header in df.columns.values:
                            reference_list.extend(list(df.loc[lines - 2:lines - 2, header].fillna(0)))

                    if reference_list == compare:
                        messages.error(self.request, "False sequence number 1 on the line " + str(lines) +".")
                        return False

                    total = 1
                    counter = 2
                    scientific_name = item[0]
                    references = item[3]
                    fooditems = [item[1]]
                    compare = reference_list
                    continue

                else:
                    counter_sum = (counter*(counter+1))/2
                    counter -= 1
                    if counter != -1 and counter_sum != total:
                        messages.error(self.request, "Check the sequence numbering on the line " + str(lines) + ".")
                        return False
            else:
                messages.error(self.request, "Sequence number on the line " + str(lines) + " is not numeric.")
                return False
        return True

    def check_measurementValue(self, df):
        import_headers = list(df.columns.values)
        if "measurementValue" in import_headers:
            for row, value in enumerate(df.loc[:, 'measurementValue'], 1):
                if pd.isnull(value) == True or any(c.isalpha() for c in str(value)) == False:
                    pass
                else:
                    messages.error(self.request, f"The measurement value on row {row} is not a number.")
                    return False
                if value <= 0:
                    messages.error(self.request, f"The measurement value on row {row} needs to be bigger than zero.")
                    return False
        elif any('verbatimTraitValue' in header for header in import_headers):
            measurement_headers = [hdr for hdr in import_headers if 'verbatimTraitValue' in hdr or 'dispersion' in hdr]
            for header in measurement_headers:
                for row, value in enumerate(df.loc[:, header], 1):
                    if pd.isnull(value) or not any(c.isalpha() for c in str(value)):
                        pass
                    else:
                        messages.error(self.request, f"The {header} \'{value}\' on row {row} is not a number.")
                        return False
                    if value < 0:
                        messages.error(self.request, f"The {header} \'{value}\' on row {row} should not be negative.")
                        return False
        return True
    
    def check_part(self, df):
        headers = list(df.columns.values)
        accepted = ['BARK', 'BLOOD', 'BONES', 'BUD', 'CARRION', 'EGGS', 'EXUDATES', 'FECES', 'FLOWER', 'FRUIT', 'LARVAE', 'LEAF', 'MINERAL', 'NECTAR/JUICE', 'NONE', 'POLLEN', 'ROOT', 'SEED', 'SHOOT', 'STEM', 'UNKNOWN', 'WHOLE']
        if 'PartOfOrganism' not in headers:
            return True
        for row, value in enumerate(df.loc[:, 'PartOfOrganism'], 1):
            if value.lower() != 'nan' and value.upper() not in accepted:
                messages.error(self.request, f"Part is invalid on row {row}. The accepted part names are: bark, blood, bones, bud, carrion, eggs, exudates, feces, flower, fruit, larvae, leaf, mineral, nectar/juice, none, pollen, root, seed, shoot, stem, unknown, whole")
                return False
        return True

    def check_reference_in_db(self, reference):
        return len(SourceReference.objects.filter(citation__iexact=reference)) == 0

    def check_references(self, df, force:bool):
        for row, ref in enumerate(df.loc[:, 'references'], 1):
            if not force:
                if not self.check_reference_in_db(ref):
                    messages.error(self.request, f"Reference on row {row} already in database. Are you sure you want to import this file? If you are sure use force upload.")
                    return False

            if len(ref) < 10 or len(ref) > 500:
                messages.error(self.request, f"Reference is too short or too long on row {row}.")
                return False
            match = re.match(r'.*([1-2][0-9]{3})', ref)
            if match is None:
                messages.error(self.request, f"Reference does not have a year number on row {row}.")
                return False
        return True
    
    def check_lengths(self, df):
        import_headers = list(df.columns.values)
        all_headers = {
           "verbatimLocality":250,
           "habitat":250,
           "samplingEffort":250,
           "verbatimEventDate":250,
           "measurementMethod":500,
           "associatedReferences":250,
           "verbatimTraitName":250,
           "verbatimTraitValue":250,
           "verbatimTraitUnit":250,
           "measurementDeterminedBy":250,
           "measurementRemarks":250,
           "measurementAccuracy":250,
           "statisticalMethod":250,
           "lifeStage":250,
           "verbatimLatitude":250,
           "verbatimLongitude":250
        }
        for header in all_headers.keys():
            if header in import_headers:
                for row, value in enumerate(df.loc[:, header], 1):
                    if len(str(value)) > all_headers[header]:
                        messages.error(self.request, f"{header} is too long on row {row}.")
                        return False
        return True

    def check_min_max(self, df):
        import_headers = list(df.columns.values)
        
        if "measurementValue_min" in import_headers:
            if "measurementValue_max" not in import_headers:
                messages.error(self.request, "There should be a header called 'measurementValue_max'.")
                return False
        elif "measurementValue_max" in import_headers:
            if "measurementValue_min" not in import_headers:
                messages.error(self.request, "There should be a header called 'measurementValue_min'.")
                return False
        
        if "measurementValue_min" not in import_headers and "measurementValue_max" not in import_headers:
            if "verbatimTraitValue" not in import_headers:
                messages.error(self.request, "There should be header called 'measurementValue_min' and 'measurementValue_max' or a header called 'verbatimTraitValue'.")
                return False
            return True
        
        if "verbatimTraitValue" in import_headers:
            counter = 1
            df_new = df[['measurementValue_min', 'measurementValue_max', 'verbatimTraitValue']]
            for value in df_new.values:
                counter += 1
                if value[0] > value[1]:
                    messages.error(self.request, "Minimum measurement value should be smaller than maximum measurement value at row " + str(counter) + ".")
                    return False
                if isinstance(value[2], float):
                    if float(value[1]) < float(value[2]):
                        messages.error(self.request, "Mean measurement value should be smaller than maximum measurement value at row " + str(counter) + ".")
                        return False
                    if float(value[0]) > float(value[2]):
                        messages.error(self.request, "Mean measurement value should be larger than minimum measurement value at row " + str(counter) + ".")
                        return False
                elif value[2][0].isalpha() or value[2][-1].isalpha():
                    if value[1] == 'nan' or pd.isnull(value[1]):
                        continue
                    if value[2] == "nan" or pd.isnull(value[2]):
                        continue
                    messages.error(self.request, "Mean value should be numeric at row " + str(counter) + ".")
                    return False
                elif float(value[1]) < float(value[2]):
                    messages.error(self.request, "Mean measurement value should be smaller than maximum measurement value at row " + str(counter) + ".")
                    return False
                elif float(value[0]) > float(value[2]):
                    messages.error(self.request, "Mean measurement value should be larger than minimum measurement value at row " + str(counter) + ".")
                    return False
        else:
            counter = 1
            df_new = df[['measurementValue_min', 'measurementValue_max']]
            for value in df_new.values:
                counter += 1
                if value[0] > value[1]:
                    messages.error(self.request, "Minimum measurement value should be smaller than maximum measurement value at row " + str(counter) + ".")
                    return False
        return True
        
def get_author(social_id):
    author = User.objects.filter(socialaccount__uid=social_id)[0]
    return author

def get_sourcereference_citation(reference, author):
    sr_old = SourceReference.objects.filter(citation__iexact=reference)
    if len(sr_old) > 0:
        return sr_old[0]
    new_reference = SourceReference(citation=reference, status=1, created_by=author)
    print(new_reference)
    new_reference.save()
    response_data = get_referencedata_from_crossref(reference)
    create_masterreference(reference, response_data, new_reference, author)
    return new_reference

def get_entityclass(taxonRank, author):
    ec_all = EntityClass.objects.filter(name__iexact=taxonRank)
    if len(ec_all) > 0:
        return ec_all[0]
    new_entity = EntityClass(name=taxonRank, created_by=author)
    print(new_entity)
    new_entity.save()
    return new_entity

def get_sourceentity(vs_name, reference, entity, author):
    se_old = SourceEntity.objects.filter(reference=reference, entity=entity, name__iexact=vs_name)
    if len(se_old) > 0:
        return se_old[0]
    new_sourceentity = SourceEntity(reference=reference, entity=entity, name=vs_name, created_by=author)
    print(new_sourceentity)
    new_sourceentity.save()
    create_new_entity_relation(new_sourceentity)
    return new_sourceentity

def get_timeperiod(sampling, ref, author):
    if sampling == 'nan':
        return None

    tp_all = TimePeriod.objects.filter(reference=ref, name__iexact=sampling)
    if len(tp_all) > 0:
        return tp_all[0]

    new_timeperiod = TimePeriod(reference=ref, name=sampling, created_by=author)
    print(new_timeperiod)
    new_timeperiod.save()
    return new_timeperiod

def get_sourcemethod(method, ref, author):
    if method == 'nan':
        return None
    sr_old = SourceMethod.objects.filter(reference=ref, name__iexact=method)
    if len(sr_old) > 0:
        return sr_old[0]

    new_sourcemethod = SourceMethod(reference=ref, name=method, created_by=author)
    print(new_sourcemethod)
    new_sourcemethod.save()
    return new_sourcemethod

def get_sourcelocation(location, ref, author):
    if location == 'nan':
        return None
    sl_old = SourceLocation.objects.filter(name__iexact=location, reference=ref)
    if len(sl_old) > 0:
        return sl_old[0]

    new_sourcelocation = SourceLocation(reference=ref, name=location, created_by=author)
    print(new_sourcelocation)
    new_sourcelocation.save()
    return new_sourcelocation

def get_choicevalue(gender):
    if gender == 'nan':
        return None
    if gender != '22' or gender != '23':
        return None
    choicevalue = ChoiceValue.objects.filter(pk=gender)
    return choicevalue[0]

def create_return_data(tsn, scientific_name, status='valid'):
    hierarchy = None
    classification_path = ""
    classification_path_ids = ""
    classification_path_ranks = ""
    if status in {'valid', 'accepted'}:
        hierarchy = itis.getFullHierarchyFromTSN(tsn)
        classification_path = itis.hierarchyToString(scientific_name, hierarchy, 'hierarchyList', 'taxonName')
        classification_path_ids = itis.hierarchyToString(tsn, hierarchy, 'hierarchyList', 'tsn', stop_index=classification_path.count("-"))
        classification_path_ranks = itis.hierarchyToString('Species', hierarchy, 'hierarchyList', 'rankName', stop_index=classification_path.count("-"))
    return_data = {
        'taxon_id': tsn,
        'canonical_form': scientific_name,
        'classification_path_ids': classification_path_ids,
        'classification_path': classification_path,
        'classification_path_ranks': classification_path_ranks,
        'taxonomic_status':status
    }
    return {'data': [{'results': [return_data]}]}

def get_accepted_tsn(tsn):
    response = itis.GetAcceptedNamesfromTSN(tsn)
    accepted_tsn = response["acceptedNames"][0]["acceptedTsn"]
    scientific_name = response["acceptedNames"][0]["acceptedName"]
    return_data = create_return_data(accepted_tsn, scientific_name)
    
    return return_data


def get_fooditem_json(food):
    query = food.lower().capitalize().replace(' ', '%20')
    url = 'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=' + query
    try:
        session = CachedSession(ITIS_CACHE, expire_after=timedelta(days=30), stale_if_error=True)
        file = session.get(url)
        data = file.text
    except (ConnectionError, UnicodeError):
        return {'data': [{}]}
    try:
        taxon_data = json.loads(data)['itisTerms'][0]
    except UnicodeDecodeError:
        taxon_data = json.loads(data.decode('utf-8', 'ignore'))['itisTerms'][0]
    return_data = {}
    if taxon_data and taxon_data['scientificName'].lower() == food.lower():
        tsn = taxon_data['tsn']
        scientific_name = taxon_data['scientificName']
        return_data = create_return_data(tsn, scientific_name, status=taxon_data['nameUsage'])
    else:
        return {'data': [{}]}
    return return_data

def create_tsn(results, tsn):
    taxonomic_unit = TaxonomicUnits.objects.filter(tsn=tsn)
    if len(taxonomic_unit)==0:
        completename = results['data'][0]['results'][0]['canonical_form']
        hierarchy_string = results['data'][0]['results'][0]['classification_path_ids']
        hierarchy = results['data'][0]['results'][0]['classification_path']
        kingdom_id = 0
        rank = 0
        
        if len(hierarchy)>0:
            kingdom = hierarchy.replace('|', '-').split('-')[0]
            kingdom_id = Kingdom.objects.filter(name=kingdom)[0].pk
            path_rank = results['data'][0]['results'][0]['classification_path_ranks'].replace('|', '-').split('-')[-1]
            rank = TaxonUnitTypes.objects.filter(rank_name=path_rank, kingdom_id=kingdom_id)[0].pk
        
        taxonomic_unit = TaxonomicUnits(tsn=tsn, kingdom_id=kingdom_id, rank_id=rank, completename=completename, hierarchy_string=hierarchy_string, hierarchy=hierarchy, common_names=None, tsn_update_date=None)
        print(taxonomic_unit)
        taxonomic_unit.save()
    else:
        taxonomic_unit = taxonomic_unit[0]

    if results['data'][0]['results'][0]['taxonomic_status'] in ("invalid", "not accepted"):
        accepted_results = get_accepted_tsn(tsn)
        accepted_taxonomic_unit = create_tsn(accepted_results, int(accepted_results['data'][0]['results'][0]['taxon_id']))
        sl_qs = itis.SynonymLinks.objects.all().filter(tsn = tsn)
        if len(sl_qs) == 0:
            sl = itis.SynonymLinks(tsn = taxonomic_unit, tsn_accepted = accepted_taxonomic_unit, tsn_accepted_name = accepted_taxonomic_unit.completename)
            print(sl)
            sl.save()
        else:
            sl = sl_qs[0]
        taxonomic_unit.hierarchy_string = accepted_taxonomic_unit.hierarchy_string
        taxonomic_unit.hierarchy = accepted_taxonomic_unit.hierarchy
        taxonomic_unit.kingdom_id = accepted_taxonomic_unit.kingdom_id
        taxonomic_unit.rank_id = accepted_taxonomic_unit.rank_id
        print(taxonomic_unit)
        taxonomic_unit.save()

    return taxonomic_unit

def create_fooditem(results, food_upper, part):
    tsn = int(results['data'][0]['results'][0]['taxon_id'])
    taxonomic_unit = create_tsn(results, tsn)
    
    name = food_upper
    if part not in {'nan', None}:
        part = ChoiceValue.objects.filter(caption=part)[0]
    else:
        part = None
    food_item = FoodItem(name=name, part=part, tsn=taxonomic_unit, pa_tsn=taxonomic_unit, is_cultivar=0)
    food_item_exists = FoodItem.objects.filter(name__iexact=name)
    if len(food_item_exists) > 0:
        return food_item_exists[0]
    print(food_item)
    food_item.save()
    return food_item

def generate_rank_id(food):
    associated_taxa = re.sub(r'\W+', ' ', food).split(' ')
    for item in associated_taxa:
        if len(item) < 3:
            associated_taxa.remove(item)
    
    rank_id = {}
    head = 0
    tail = 0
    while True:
        if head == tail:
            query = associated_taxa[tail]
            head += 1
        else:
            query = associated_taxa[tail] + " " +associated_taxa[head]
            tail += 1
        results = get_fooditem_json(query)
        if len(results['data'][0]) > 0:
            rank = int(itis.getTaxonomicRankNameFromTSN(results['data'][0]['results'][0]['taxon_id'])['rankId'])
            rank_id[rank] = results
            break
        if head >= len(associated_taxa):
            break
    return rank_id

def get_fooditem(food, part):
    food_upper = food.upper()
    food_item = FoodItem.objects.filter(name__iexact=food_upper)
    
    if len(food_item) > 0:
        return food_item[0]
    
    rank_id = generate_rank_id(food)

    if len(rank_id) == 0:
        if part not in {'nan', None}:
            part = ChoiceValue.objects.filter(caption=part.upper())[0]
        else:
            part = None
        food_item = FoodItem(name=food_upper, part=part, tsn=None, pa_tsn=None, is_cultivar=0)
        print(food_item)
        food_item.save()
        return food_item
    return create_fooditem(rank_id[max(rank_id)], food_upper, part)

def possible_nan_to_zero(size):
    if size != size or size == 'nan':
        return 0
    return size

def possible_nan_to_none(possible):
    if possible != possible or possible == 'nan':
        return None
    return possible


@transaction.atomic
def create_dietset(row, df):
    headers = list(df.columns.values)
    author = get_author(getattr(row, 'author'))
    print(author)
    reference = get_sourcereference_citation(getattr(row, 'references'), author)
    print(reference)
    entityclass = get_entityclass(getattr(row, 'taxonRank'), author)
    print(entityclass)
    taxon =  get_sourceentity(getattr(row, 'verbatimScientificName'), reference, entityclass, author)
    if 'verbatimLocality' in headers:
        location = get_sourcelocation(getattr(row, 'verbatimLocality'), reference, author)
        print(location)
    else:
        location = None
    if 'sex' in headers:
        gender = get_choicevalue(getattr(row, 'sex'))
    else:
        gender = None
        print(gender)
    if 'individualCount' in headers:
        sample_size = possible_nan_to_zero(getattr(row, 'individualCount'))
        print(sample_size)
    else:
        sample_size = 0
    if 'associatedReferences' in headers:
        cited_reference =  possible_nan_to_none(getattr(row, 'associatedReferences'))
        print(cited_reference)
    else:
        cited_reference = None
    if 'samplingEffort' in headers:
        time_period = get_timeperiod(getattr(row, 'samplingEffort'), reference, author)
        print(time_period)
    else:
        time_period = None
    if 'measurementMethod' in headers:
        method =  get_sourcemethod(getattr(row, 'measurementMethod'), reference, author)
        print(method)
    else:
        method = None
    if 'verbatimEventDate' in headers:
        study_time = possible_nan_to_none(getattr(row, 'verbatimEventDate'))
        print(study_time)
    else:
        study_time = None

    ds_old = DietSet.objects.filter(
        reference=reference,
        taxon=taxon,
        location=location,
        gender=gender,
        sample_size=sample_size,
        cited_reference=cited_reference,
        time_period=time_period,
        method=method,
        study_time=study_time,
        created_by=author
    )
    print(str(ds_old.query))

    if len(ds_old) > 0:
        ds = ds_old[0]
    else:
        ds = DietSet(
            reference=reference,
            taxon=taxon,
            location=location,
            gender=gender,
            sample_size=sample_size,
            cited_reference=cited_reference,
            time_period=time_period,
            method=method,
            study_time=study_time,
            created_by=author
        )
        print(ds)
        ds.save()

    create_dietsetitem(row, ds, headers)

@transaction.atomic
def create_dietsetitem(row, diet_set, headers):
    if 'PartOfOrganism' in headers:
        food_item = get_fooditem(getattr(row, 'verbatimAssociatedTaxa'), possible_nan_to_none(getattr(row, 'PartOfOrganism')))
    else:
        food_item = get_fooditem(getattr(row, 'verbatimAssociatedTaxa'), None)
    list_order = getattr(row, 'sequence')
    if 'measurementValue' in headers:
        percentage = round(possible_nan_to_zero(getattr(row, 'measurementValue')), 3)
    else:
        percentage = 0
#    old_ds = DietSetItem.objects.filter(diet_set=diet_set, food_item=food_item, list_order=list_order, percentage=percentage)
    old_ds = DietSetItem.objects.filter(diet_set=diet_set, food_item=food_item, list_order=list_order)
#    print(str(old_ds.query))
#    print(diet_set.id, food_item.id, list_order, percentage)
    if len(old_ds) == 0:
        dietsetitem = DietSetItem(diet_set=diet_set, food_item=food_item, list_order=list_order, percentage=percentage) 
        print(dietsetitem)
        dietsetitem.save()

def trim(text:str):
    return " ".join(text.split())

def trim_df(df):
    headers = df.columns
    for i, row in df.iterrows():
        for header in headers:
            df.at[i, header] = trim(str(df.at[i, header]))

# Search citation from CrossrefApi: https://api.crossref.org/swagger-ui/index.htm
# Please do not make any unnessecary queries: https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/
def get_referencedata_from_crossref(citation): # pragma: no cover
    c = citation.replace(" ", "%20")
    url = 'https://api.crossref.org/works?query.bibliographic=%22'+c+'%22&mailto=kari.lintulaakso@helsinki.fi&rows=2'
    try:
        x = requests.get(url, timeout=300)
        y = x.json()
        return y
    except requests.exceptions.RequestException as e:
        print('Error: ', e)
        return None

def title_matches_citation(title, source_citation):
    # https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
    title_without_html = re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', '', title)
    title_without_space = re.sub(r'\s+', '', title_without_html)
    source_citation_without_html = re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', '', source_citation)
    source_citation_without_space = re.sub(r'\s+', '', source_citation_without_html)

    if title_without_space.lower() not in source_citation_without_space.lower():
        return False
    return True

def create_masterreference(source_citation, response_data, sr, user_author):
    try:
        if response_data['message']['total-results'] == 0:
            return False
        doi = None
        uri = None
        year = None
        container_title = None
        volume = None
        issue = None
        page = None
        citation = None
        ref_type = None
        x = response_data['message']['items'][0]
        fields = []
        for field_name in x:
            fields.append(field_name)
        if 'title' not in fields:
            return False
        if not title_matches_citation(x['title'][0], source_citation):
            return False
        title = re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', '', x['title'][0])
        if 'author' not in fields:
            return False
        authors = []
        for a in x['author']:
            author = a['family'] + ", " + a['given'][0] + "."
            authors.append(author)
        first_author = x['author'][0]['family'] + ", " + x['author'][0]['given'][0] + "."
        if 'DOI' in fields:
            doi = x['DOI']
        if 'uri' in fields:
            uri = x['uri']
        if 'published' in fields:
            year = x['published']['date-parts'][0][0]
        if 'container-title' in fields:
            container_title = x['container-title'][0]
        if 'volume' in fields:
            volume = x['volume']
        if 'issue' in fields:
            issue = x['issue']
        if 'page' in fields:
            page = x['page']
        if 'type' in fields:
            ref_type = x['type']
            if ref_type == 'journal-article':
                citation = make_harvard_citation_journalarticle(title, doi, authors, year, container_title, volume, issue, page)
            else:
                citation = ""
                for a in authors:
                    if authors.index(a) == len(authors) - 1:
                        citation += str(a)
                    else:
                        citation += str(a) + ", "
                citation += " " + str(year) + ". " + str(title) + ". Available at: " + str(doi) + "."

        mr = MasterReference(
            type=ref_type,
            doi=doi,
            uri=uri,
            first_author=first_author,
            year=year,
            title=title,
            container_title=container_title,
            volume=volume,
            issue=issue,
            page=page,
            citation=citation,
            created_by=user_author
        )
        print(mr)
        mr.save()
        sr.master_reference = mr
        print(sr)
        sr.save()
        return True
    except DatabaseError as db_err:
        raise db_err
    except Exception as e:
        return False


def make_harvard_citation_journalarticle(title, d, authors, year, container_title, volume, issue, page):
    citation = ""
    for a in authors:
        if authors.index(a) == len(authors) - 1:
            citation += str(a)
        else:
            citation += str(a) + ", "
    
    citation += " " + str(year) + ". " + str(title) + ". " + str(container_title) + ". " + str(volume) + "(" + str(issue) + "), pp." + str(page) + ". Available at: " + str(d) + "." 
    return citation

def api_query_globalnames_by_name(name):
    trimmed_name = name.replace(" ", "%20")
    url = "https://resolver.globalnames.org/name_resolvers.json?names="+trimmed_name.capitalize()+"&data_source_ids=174"
    result = requests.get(url, timeout=300)
    return result.json()

def check_entity_realtions(source_entity):
    try:
        found_entity_relation = EntityRelation.objects.is_active().filter(
            source_entity__name__iexact=source_entity.name).filter(
            data_status_id=5).filter(
            master_entity__reference_id=4).filter(
            relation__name__iexact='Taxon Match')
        return found_entity_relation
    except:
        print('Error searching entity relation', sys.exc_info(),traceback.format_exc())


def create_new_entityrelation_with_api_data(source_entity):
    api_result = get_fooditem_json(source_entity.name)["data"][0]
    if api_result:
        canonical_form = api_result["results"][0]["canonical_form"]
        master_entity_result = MasterEntity.objects.filter(name=canonical_form, entity_id=source_entity.entity_id,reference_id=4)
        if master_entity_result:
            EntityRelation(master_entity=master_entity_result[0],
                            source_entity=source_entity.id,
                            relation_id=1,
                            data_status_id=5,
                            relation_status_id=1,
                            remarks=master_entity_result[0].reference).save()
    else:
        return


def create_new_entity_relation(source_entity):
    try:
        result = check_entity_realtions(source_entity)
        if len(result) < 1:
            create_new_entityrelation_with_api_data(source_entity)
        else:
            try:
                EntityRelation(master_entity=result[0].master_entity
                            ,source_entity=source_entity
                            ,relation=result[0].relation
                            ,data_status=result[0].data_status
                            ,relation_status=result[0].relation_status
                            ,remarks=result[0].remarks).save()
            except:
                print('Error creating new entity relation ', sys.exc_info(), traceback.format_exc())
    except:
        print('Error creating new entity relation', sys.exc_info(), traceback.format_exc())

@transaction.atomic
def create_ets(row, headers):
    author = get_author(getattr(row, 'author'))
    reference = get_sourcereference_citation(getattr(row, 'references'), author)
    entityclass = get_entityclass(getattr(row, 'taxonRank'), author)
    taxon =  get_sourceentity(getattr(row, 'verbatimScientificName'), reference, entityclass, author)
    name = possible_nan_to_none(getattr(row, 'verbatimTraitName'))
    verbatimTraitUnit = getattr(row, 'verbatimTraitUnit')

    if 'measurementMethod' in headers:
        method = get_sourcemethod(getattr(row, 'measurementMethod'), reference, author)
    else:
        method = None
    if 'measurementRemarks' in headers:
        remarks = possible_nan_to_none(getattr(row, 'measurementRemarks'))
    else:
        remarks = None

    if verbatimTraitUnit == 'nan' or verbatimTraitUnit != verbatimTraitUnit or verbatimTraitUnit == 'NA':
        entityclass = get_entityclass('Taxon', author)
        attribute = get_sourceattribute(name, reference, entityclass, method, 2, author)
        if 'verbatimTraitValue' in headers:
            vt_value = possible_nan_to_none(getattr(row, 'verbatimTraitValue'))
        else:
            vt_value = None
        choicesetoption = get_sourcechoicesetoption(vt_value, attribute, author)
        choicesetoptionvalue = get_sourcechoicesetoptionvalue(taxon, choicesetoption, author)

    else:  
        entityclass = get_entityclass('Taxon', author)
        attribute = get_sourceattribute(name, reference, entityclass, method, 1, author)
        unit = get_sourceunit(verbatimTraitUnit, author)
        if 'verbatimTraitValue' in headers:
            vt_value = possible_nan_to_zero(getattr(row, 'verbatimTraitValue'))
        else:
            vt_value = 0
        choicesetoption = get_sourcechoicesetoption(vt_value, attribute, author)
        if 'verbatimLocality' in headers:
            locality = get_sourcelocation(getattr(row, 'verbatimLocality'), reference, author)
        else:
            locality = None
        if 'statisticalMethod' in headers:
            statistic = get_sourcestatistic(getattr(row, 'statisticalMethod'), reference, author)
        else:
            statistic = None
        if 'associatedReferences' in headers:
            cited_reference = possible_nan_to_none(getattr(row, 'associatedReferences'))
        else:
            cited_reference = None
        if 'measurementValue_min' and 'measurementValue_max' in headers:
            mes_min = possible_nan_to_zero(getattr(row, 'measurementValue_min'))
            mes_max = possible_nan_to_zero(getattr(row, 'measurementValue_max'))
        else:
            mes_min = 0
            mes_max = 0
        if 'dispersion' in headers:
            std = possible_nan_to_zero(getattr(row, 'dispersion'))
        else:
            std = 0
        if 'lifeStage' in headers:
            lifestage = get_choicevalue_ets(getattr(row, 'lifeStage'), 'Lifestage', author)
        else:
            lifestage = None
        if 'measurementDeterminedBy' in headers:
            measured_by = possible_nan_to_none(getattr(row, 'measurementDeterminedBy'))
        else:
            measured_by = None
        if 'measurementAccuracy' in headers:
            accuracy = possible_nan_to_none(getattr(row, 'measurementAccuracy'))
        else:
            accuracy = None
        if 'individualCount' in headers:
            count = possible_nan_to_zero(getattr(row, 'individualCount'))
        else:
            count = 0
        if 'sex' in headers:
            gender = get_choicevalue_ets(getattr(row, 'sex'), 'Gender', author)
        else:
            gender = None
        create_sourcemeasurementvalue(taxon, attribute, locality, count, mes_min, mes_max, std, vt_value, statistic,
                                      unit, gender, lifestage, accuracy, measured_by, remarks, cited_reference, author)
        return

@transaction.atomic
def create_proximate_analysis(row, df):
    headers = list(df.columns.values)
    author = get_author(getattr(row, 'author'))
    attribute_dict = {
        "reference" : get_sourcereference_citation(getattr(row, 'references'), author),
        "method" : None,
        "location" : None,
        "study_time" : None,
        "cited_reference" : None
    }
    if "measurementMethod" in headers:
        attribute_dict["method"] = get_sourcemethod(getattr(row, "measurementMethod"), attribute_dict["reference"], author)
    if "verbatimLocality" in headers:
        attribute_dict["location"] = get_sourcelocation(getattr(row, "verbatimLocality"), attribute_dict["reference"], author)
    if "verbatimEventDate" in headers:
        attribute_dict["study_time"] = getattr(row, "verbatimEventDate")
    if "associatedReferences" in headers:
        attribute_dict["cited_reference"] = getattr(row, "associatedReferences")
    pa = None
    pa_old = ProximateAnalysis.objects.filter(**attribute_dict)
    if len(pa_old) > 0:
        pa = pa_old[0]
    else:
        pa = ProximateAnalysis(**attribute_dict)
        pa.save()
    create_proximate_analysis_item(row, pa, attribute_dict["location"], attribute_dict["cited_reference"], headers)

@transaction.atomic
def create_proximate_analysis_item(row, pa, location, cited_reference, headers):
    #Names of the import fields in the model.
    pa_item_dict = {
        "proximate_analysis" : pa,
        "location" : location,
        "cited_reference" : cited_reference,
        "forage" : get_fooditem(
            getattr(row, 'verbatimScientificName'),
            possible_nan_to_none(getattr(row, "PartOfOrganism"))
        )
    }
    
    #Check if pa_item already exists
    pa_item_old = ProximateAnalysisItem.objects.filter(**pa_item_dict)
    pa_item_dict = convert_empty_values_pa(row, headers, pa_item_dict)
    pa_item_dict = generate_standard_values_pa(pa_item_dict)
    if len(pa_item_old) > 0:
        pa_item_old.update(**pa_item_dict)
    else:
        pa_item = ProximateAnalysisItem(**pa_item_dict)
        pa_item.save()

def convert_empty_values_pa(row, headers, pa_item_dict):
    pa_item_dict_new = pa_item_dict

    proximate_analysis_item_headers = {
        "individualCount":{
            "name":"sample_size",
            "type":int
        },
        "measurementDeterminedBy":{
            "name":"measurement_determined_by",
            "type":str
        },
        "measurementRemarks":{
            "name":"measurement_remarks",
            "type":str
        },
        "verbatimTraitValue__moisture":{
            "name":"moisture_reported",
            "type":float
        },
        "dispersion__moisture":{
            "name":"moisture_dispersion",
            "type":float
        },
        "measurementMethod__moisture":{
            "name":"moisture_measurement_method",
            "type":str
        },
        "verbatimTraitValue__dry_matter":{
            "name":"dm_reported",
            "type":float
        },
        "dispersion__dry_matter":{
            "name":"dm_dispersion",
            "type":float
        },
        "measurementMethod__dry_matter":{
            "name":"dm_measurement_method",
            "type":str
        },
        "verbatimTraitValue__ether_extract":{
            "name":"ee_reported",
            "type":float
        },
        "dispersion__ether_extract":{
            "name":"ee_dispersion",
            "type":float
        },
        "measurementMethod__ether_extract":{
            "name":"ee_measurement_method",
            "type":str
        },
        "verbatimTraitValue__crude_protein":{
            "name":"cp_reported",
            "type":float
        },
        "dispersion__crude_protein":{
            "name":"cp_dispersion",
            "type":float
        },
        "measurementMethod__crude_protein":{
            "name":"cp_measurement_method",
            "type":str
        },
        "verbatimTraitValue__crude_fibre":{
            "name":"cf_reported",
            "type":float
        },
        "dispersion__crude_fibre":{
            "name":"cf_dispersion",
            "type":float
        },
        "measurementMethod__crude_fibre":{
            "name":"cf_measurement_method",
            "type":str
        },
        "verbatimTraitValue_ash":{
            "name":"ash_reported",
            "type":float
        },
        "dispersion__ash":{
            "name":"ash_dispersion",
            "type":float
        },
        "measurementMethod_ash":{
            "name":"ash_measurement_method",
            "type":str
        },
        "verbatimTraitValue__nitrogen_free_extract":{
            "name":"nfe_reported",
            "type":float
        },
        "dispersion__nitrogen_free_extract":{
            "name":"nfe_dispersion",
            "type":float
        },
        "measurementMethod__nitrogen_free_extract":{
            "name":"nfe_measurement_method",
            "type":str
        },
        "associatedReferences":{
            "name":"cited_reference",
            "type":str
        }
    }
    
    for header in proximate_analysis_item_headers.keys():
        if header in headers:
            value = getattr(row, header)
            value = possible_nan_to_none(value)
            pa_item_dict_new[proximate_analysis_item_headers[header]["name"]] = value

    return pa_item_dict_new

def generate_standard_values_pa(items):
    standard_items = items
    remarks_text = "CP+EE+CF+NFE+ASH = 100"
    # Sum of reported values excluding dry matter and moisture
    item_sum = Decimal(0.0)
    for item in items.keys():
        if "reported" in item and "dm" not in item and "moisture" not in item and items[item] is not None:
            item_sum += Decimal(items[item])
    
    # If reported values sum to 1000 instead of 100 then divide sum by 10
    sum_to_thousand = False
    if abs(item_sum - Decimal(100)) > abs(item_sum - Decimal(1000)):
        sum_to_thousand = True
        remarks_text = "CP+EE+CF+NFE+ASH = 1000"
        item_sum /= Decimal(10)

    # If the sum of reported values is closer to 100 when moisture is included then add moisture to the sum
    if items["moisture_reported"] is not None:
        if sum_to_thousand and abs(Decimal(100) - (item_sum + (Decimal(items["moisture_reported"]) / Decimal(10)))) < abs(Decimal(100) - item_sum):
            item_sum += Decimal(items["moisture_reported"]) / Decimal(10)
            remarks_text = "Moisture+CP+EE+CF+NFE+ASH = 1000"
        elif abs(Decimal(100) - (item_sum + Decimal(items["moisture_reported"]))) < abs(Decimal(100) - item_sum):
            item_sum += Decimal(items["moisture_reported"])
            remarks_text = "Moisture+CP+EE+CF+NFE+ASH = 100"
    elif items["dm_reported"] is not None:
        if abs(item_sum - Decimal(items["dm_reported"])) < Decimal(0.001):
            remarks_text = "CP+EE+CF+NFE+ASH = DM"
    
    for item in list(items.keys()):
        if "reported" not in item or "dm" in item or "moisture" in item:
            continue
        elif items[item] is None:
            standard_items[item.replace("reported","std")] = None
        elif sum_to_thousand:
            standard_items[item.replace("reported","std")] = ((Decimal(items[item]) / Decimal(10)) / item_sum) * Decimal(100)
        else:
            standard_items[item.replace("reported","std")] = (Decimal(items[item]) / item_sum) * Decimal(100)

    standard_items["remarks"] = remarks_text
    standard_items["transformation"] = "Original value / (CP+EE+CF+ASH+NFE) * 100"
    
    return standard_items

def create_sourcemeasurementvalue_no_gender(taxon, attribute, locality, count, mes_min, mes_max, std, vt_value,
                                            statistic, unit, lifestage, accuracy, measured_by, remarks,
                                            cited_reference, author):
    smv_old = SourceMeasurementValue.objects.filter(
        source_entity=taxon,
        source_attribute=attribute,
        source_location=locality,
        n_total=count, n_unknown=count,
        minimum=mes_min, maximum=mes_max,
        std=std, mean=vt_value,
        source_statistic=statistic,
        source_unit=unit,
        life_stage=lifestage,
        measurement_accuracy__iexact=accuracy,
        measured_by__iexact=measured_by,
        remarks__iexact=remarks,
        cited_reference__iexact=cited_reference
    )
    if len(smv_old) > 0:
        return
    sm_value = SourceMeasurementValue(
        source_entity=taxon,
        source_attribute=attribute,
        source_location=locality,
        n_total=count, n_unknown=count,
        minimum=mes_min, maximum=mes_max,
        std=std,  mean=vt_value,
        source_statistic=statistic,
        source_unit=unit,
        life_stage=lifestage,
        measurement_accuracy=accuracy,
        measured_by=measured_by,
        remarks=remarks,
        cited_reference=cited_reference,
        created_by=author
    )
    print(sm_value)
    sm_value.save()

def create_sourcemeasurementvalue(taxon, attribute, locality, count, mes_min, mes_max, std, vt_value, statistic, unit,
                                  gender, lifestage, accuracy, measured_by, remarks, cited_reference, author):
    n_female = 0
    n_male = 0
    n_unknown = 0
    if isinstance(gender, type(None)):
        create_sourcemeasurementvalue_no_gender(taxon, attribute, locality, count, mes_min, mes_max, std, vt_value,
                                                statistic, unit, lifestage, accuracy, measured_by, remarks,
                                                cited_reference, author)
        return 
    if gender.caption.lower() == 'female':
        n_female = count
    elif gender.caption.lower() == 'male':
        n_male = count
    else:
        n_unknown = count     
    smv_old = SourceMeasurementValue.objects.filter(
        source_entity=taxon,
        source_attribute=attribute,
        source_location=locality,
        n_total=count,
        n_female=n_female,
        n_male=n_male,
        n_unknown=n_unknown,
        minimum=mes_min,
        maximum=mes_max,
        std=std,
        mean=vt_value,
        source_statistic=statistic,
        source_unit=unit,
        gender=gender,
        life_stage=lifestage,
        measurement_accuracy__iexact=accuracy,
        measured_by__iexact=measured_by,
        remarks__iexact=remarks,
        cited_reference__iexact=cited_reference
    )
    if len(smv_old) > 0:
        return
    sm_value = SourceMeasurementValue(
        source_entity=taxon,
        source_attribute=attribute,
        source_location=locality,
        n_total=count,
        n_female=n_female,
        n_male=n_male,
        n_unknown=n_unknown,
        minimum=mes_min,
        maximum=mes_max,
        std=std,
        mean=vt_value,
        source_statistic=statistic,
        source_unit=unit,
        gender=gender,
        life_stage=lifestage,
        measurement_accuracy=accuracy,
        measured_by=measured_by, remarks=remarks,
        cited_reference=cited_reference,
        created_by=author
    )
    print(sm_value)
    sm_value.save()
    return

def get_choicevalue_ets(choice, choice_set, author):
    if choice != choice or choice == 'nan':
        return None
    choiceset_obj = ChoiceValue.objects.filter(caption__iexact=choice, choice_set__iexact=choice_set)
    if len(choiceset_obj) > 0:
        return choiceset_obj[0]
    cv = ChoiceValue.objects.create(caption=choice, choice_set=choice_set, created_by=author)
    return cv

def get_sourceunit(unit, author):
    if unit != unit or unit == 'nan':
        return None
    su_old = SourceUnit.objects.filter(name__iexact=unit)
    if len(su_old) > 0:
        return su_old[0]
    su = SourceUnit(name=unit, created_by=author)
    print(su)
    su.save()
    return su

def get_sourcechoicesetoptionvalue(entity, sourcechoiceoption, author):
    scov_old = SourceChoiceSetOptionValue.objects.filter(
        source_entity=entity, source_choiceset_option=sourcechoiceoption
    )
    if len(scov_old) > 0:
        return scov_old[0]
    scov = SourceChoiceSetOptionValue(
        source_entity=entity, source_choiceset_option=sourcechoiceoption, created_by=author
    )
    print(scov)
    scov.save()
    return scov

def get_sourcechoicesetoption(name, attribute, author):
    if name == 'nan' or name == 'NA' or name != name:
        return None
    sco_old = SourceChoiceSetOption.objects.filter(source_attribute=attribute, name__iexact=name)
    if len(sco_old) > 0:
        return sco_old[0]
    sco = SourceChoiceSetOption(source_attribute=attribute, name=name, created_by=author)
    print(sco)
    sco.save()
    return sco

def get_sourcestatistic(statistic, ref, author):
    if statistic != statistic or statistic == 'nan':
        return None
    ss_old = SourceStatistic.objects.filter(name__iexact=statistic, reference=ref)
    if len(ss_old) > 0:
        return ss_old[0]
    ss = SourceStatistic(name=statistic, reference=ref, created_by=author)
    print(ss)
    ss.save()
    return ss

def get_sourceattribute(name, ref, entity, method, type_value, author):
    sa_old = SourceAttribute.objects.filter(
        name__iexact=name, reference=ref, entity=entity, method=method, type=type_value
    )
    if len(sa_old) > 0:
        return sa_old[0]
    sa = SourceAttribute(name=name, reference=ref, entity=entity, method=method, type=type_value, created_by=author)
    print(sa)
    sa.save()
    return sa
