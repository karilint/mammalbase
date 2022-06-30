from doctest import master
from multiprocessing.spawn import import_main_path
from mb.models import ChoiceValue, DietSet, EntityClass, MasterReference, SourceAttribute, SourceChoiceSetOptionValue, SourceChoiceSetOption, SourceEntity, SourceLocation, SourceMeasurementValue, SourceMethod, SourceReference, SourceStatistic, SourceUnit, TimePeriod, DietSetItem, FoodItem ,EntityRelation, MasterEntity
from itis.models import TaxonomicUnits, Kingdom, TaxonUnitTypes
from django.contrib import messages
from django.db import transaction
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
import itis.views as itis

import pandas as pd
import re, json, urllib.request, requests, sys, traceback

import sys, traceback

class Check:
    def __init__(self, request):
        self.request = request
        self.id = None

    def check_all_ds(self, df, force=False):
        if self.check_headers_ds(df) == False:
            return False
        elif self.check_author(df) == False:
            return False
        elif self.check_verbatimScientificName(df) == False:
            return False
        elif self.check_taxonRank(df) == False:
            return False
        elif self.check_verbatim_associated_taxa(df) == False:
            return False
        elif self.check_sequence(df) == False:
            return False
        elif self.check_measurementValue(df) == False:
            return False
        elif self.check_part(df) == False:
            return False
        elif self.check_references(df, force) == False:
            return False
        elif self.check_lengths(df) == False:
            return False
        return True
    
    def check_all_ets(self, df):
        if self.check_headers_ets(df) == False:
            return False
        elif self.check_author(df) == False:
            return False
        elif self.check_verbatimScientificName(df) == False:
            return False
        elif self.check_taxonRank(df) == False:
            return False
        elif self.check_lengths(df) == False:
           return False
        elif self.check_min_max(df) == False:
            return False
        return True

    def check_valid_author(self, df):
        counter = 1
        for author in (df.loc[:, 'author']):
            counter += 1
            if author == "nan":
                messages.error(self.request, "The author is empty at row " +  str(counter) + ".")
                return False
            data = SocialAccount.objects.all().filter(uid=author)
            if data.exists() == False:
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

    def check_author(self, df):
        numbers = []
        counter = 1
        for author in (df.loc[:, 'author']):
            counter += 1
            if len(str(author)) != 19:
                messages.error(self.request, "The author on the line number " + str(counter) + " is not in the correct form.")
                return False
            if "X" in author:
                author = author.replace("X", "")
            numbers.append(author.replace("-", ""))
    
        counter = 1
        for number in numbers:
            counter += 1
            if not number.isdigit():
                messages.error(self.request, "The author on the line number " + str(counter) + " is not in the correct form.")
                return False
        return True

    def check_verbatimScientificName(self, df):
        counter = 1
        for name in df.loc[:, 'verbatimScientificName']:
            counter += 1
            if name == "nan" or pd.isna(name):
                messages.error(self.request, "Scientific name is empty at row " + str(counter) + ".")
                return False
            if len(name) > 250:
                messages.error(self.request, "Scientific name is too long at row " + str(counter) + ".")
                return False

        df_new = df[['verbatimScientificName', 'taxonRank']]
        counter = 1
        for item in df_new.values:
            counter += 1
            names_list = item[0].split()

            if len(names_list) > 3 and "sp." not in names_list and "sp" not in names_list and "cf." not in names_list and "cf" not in names_list and "indet." not in names_list and "indet" not in names_list and "aff." not in names_list and "aff" not in names_list and "spp." not in names_list and "spp" not in names_list:
                messages.error(self.request, "Scientific name is not in the correct format on the line " + str(counter) + ".")
                return False
            if len(names_list) == 3 and item[1] not in ['Subspecies', 'subspecies'] and "sp." not in names_list and "sp" not in names_list and "cf." not in names_list and "cf" not in names_list and "indet." not in names_list and "indet" not in names_list and "aff." not in names_list and "aff" not in names_list and "aff." not in names_list and "aff" not in names_list and "spp." not in names_list and "spp" not in names_list:
                messages.error(self.request, "Scientific name is not in the correct format or taxonomic rank should be 'Subspecies' on the line " + str(counter) + ".")
                return False
            if len(names_list) == 2 and item[1] not in ['Species', 'species'] and "sp." not in names_list and "sp" not in names_list and "cf." not in names_list and "cf" not in names_list and "indet." not in names_list and "indet" not in names_list and "aff." not in names_list and "aff" not in names_list and "aff." not in names_list and "aff" not in names_list and "spp." not in names_list and "spp" not in names_list:
                messages.error(self.request, "Scientific name is not in the correct format or taxonomic rank should be 'Species' on the line " + str(counter) + ".")
                return False
            if len(names_list) == 1 and item[1] not in ['Genus', 'genus'] and "sp." not in names_list and "sp" not in names_list and "cf." not in names_list and "cf" not in names_list and "indet." not in names_list and "indet" not in names_list and "aff." not in names_list and "aff" not in names_list and "aff." not in names_list and "aff" not in names_list and "spp." not in names_list and "spp" not in names_list:
                messages.error(self.request, "Scientific name is not in the correct format or taxonomic rank should be 'Genus' on the line " + str(counter) + ".")
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
        counter = 0
        total = 1
        fooditems = []
        lines = 1
        compare = []

        for item in df_new.values:
           
            lines += 1
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

                else:
                    if int(item[2]) == 1:
                        reference_list = [item[0], item[3]]
                        if has_measurementvalue:
                            measurementvalue_reference = item[4]
                        if 'verbatimLocality' in df.columns.values:
                            for vl in df.loc[(lines-2):(lines-2), 'verbatimLocality'].fillna(0):
                                reference_list.append(vl)
                        if 'habitat' in df.columns.values:
                            for hab in df.loc[(lines-2):(lines-2), 'habitat'].fillna(0):
                                reference_list.append(hab)
                        if 'samplingEffort' in df.columns.values:
                            for se in df.loc[(lines-2):(lines-2), 'samplingEffort'].fillna(0):
                                reference_list.append(se)
                        if 'sex' in df.columns.values:
                            for sex in df.loc[(lines-2):(lines-2), 'sex'].fillna(0):
                                reference_list.append(sex)
                        if 'individualCount' in df.columns.values:
                            for ic in df.loc[(lines-2):(lines-2), 'individualCount'].fillna(0):
                                reference_list.append(ic)
                        if 'verbatimEventDate' in df.columns.values:
                            for ved in df.loc[(lines-2):(lines-2), 'verbatimEventDate'].fillna(0):
                                reference_list.append(ved)
                        if 'measurementMethod' in df.columns.values:
                            for mm in df.loc[(lines-2):(lines-2), 'measurementMethod'].fillna(0):
                                reference_list.append(mm)
                        if 'associatedReferences' in df.columns.values:
                            for ar in df.loc[(lines-2):(lines-2), 'associatedReferences'].fillna(0):
                                reference_list.append(ar)
                        if reference_list == compare:
                            messages.error(self.request, "False sequence number 1 on the line " + str(lines) +".")
                            return False
                    
                        total = 1
                        counter = 2
                        scientific_name = item[0]
                        references = item[3]
                        fooditems = [item[1]]
                        compare = [item[0], item[3]]
                    
                        if 'verbatimLocality' in df.columns.values:
                            for vl in df.loc[(lines-2):(lines-2), 'verbatimLocality'].fillna(0):
                                compare.append(vl)
                        if 'habitat' in df.columns.values:
                            for hab in df.loc[(lines-2):(lines-2), 'habitat'].fillna(0):
                                compare.append(hab)
                        if 'samplingEffort' in df.columns.values:
                            for se in df.loc[(lines-2):(lines-2), 'samplingEffort'].fillna(0):
                                compare.append(se)
                        if 'sex' in df.columns.values:
                            for sex in df.loc[(lines-2):(lines-2), 'sex'].fillna(0):
                                compare.append(sex)
                        if 'individualCount' in df.columns.values:
                            for ic in df.loc[(lines-2):(lines-2), 'individualCount'].fillna(0):
                                compare.append(ic)
                        if 'verbatimEventDate' in df.columns.values:
                            for ved in df.loc[(lines-2):(lines-2), 'verbatimEventDate'].fillna(0):
                                compare.append(ved)
                        if 'measurementMethod' in df.columns.values:
                            for mm in df.loc[(lines-2):(lines-2), 'measurementMethod'].fillna(0):
                                compare.append(mm)
                        if 'associatedReferences' in df.columns.values:
                            for ar in df.loc[(lines-2):(lines-2), 'associatedReferences'].fillna(0):
                                compare.append(ar)
                        continue
                
                    else:
                        sum = (counter*(counter+1))/2
                        counter -= 1
                        if counter != -1 and sum != total:
                            messages.error(self.request, "Check the sequence numbering on the line " + str(lines) + ".")
                            return False                
            else:
                messages.error(self.request, "Sequence number on the line " + str(lines) + " is not numeric.")
                return False
        return True

    def check_measurementValue(self, df):
        import_headers = list(df.columns.values)
        if "measurementValue" not in import_headers:
            return True
    
        counter = 1
        for value in (df.loc[:, 'measurementValue']):
            counter += 1
            if pd.isnull(value) == True or any(c.isalpha() for c in str(value)) == False:
                pass
            else:
                messages.error(self.request, "The measurement value on the line " + str(counter) + " is not a number.")
                return False
            if value <= 0:
                messages.error(self.request, "The measurement value on the line " + str(counter) + " needs to be bigger than zero.")
                return False

        return True
    
    def check_part(self, df):
        headers = list(df.columns.values)
        accepted = ['BANK', 'BLOOD', 'BONES', 'BUD', 'CARRION', 'EGGS', 'EXUDATES', 'FECES', 'FLOWER', 'FRUIT', 'LARVAE', 'LEAF', 'MINERAL', 'NECTAR/JUICE', 'NONE', 'POLLEN', 'ROOT', 'SEED', 'SHOOT', 'STEM', 'WHOLE']
        if 'PartOfOrganism' not in headers:
            return True
        counter = 1
        for value in (df.loc[:, 'PartOfOrganism']):
            counter += 1
            if value.lower() != 'nan':
                if value.upper() not in accepted:
                    messages.error(self.request, "Part is in the wrong form on the line " + str(counter) + " The correct are: bank. blood, bones, bud, carrion, eggs, exudates, feces, flower, fruit, larvae, leaf, mineral, nectar/juice, none, pollen, root, seed, shoot, stem, whole")
                    return False
        return True

    def check_reference_in_db(self, reference):
        return len(SourceReference.objects.filter(citation__iexact=reference)) == 0

    def check_references(self, df, force:bool):
        counter = 1
        for ref in (df.loc[:, 'references']):
            if not force:
                if not self.check_reference_in_db(ref):
                    messages.error(self.request, "Reference in line "+ str(counter) +" already in database. Are you sure you want to import this file? If you are sure use force upload.")
                    return False

            if len(ref) < 10 or len(ref) > 500:
                messages.error(self.request, "Reference is too short or too long on the line " + str(counter) + ".")
                return False
            match = re.match(r'.*([1-2][0-9]{3})', ref)
            counter += 1
            if match is None:
                messages.error(self.request, "Reference does not have a year number on the line " + str(counter) + ".")
                return False

        return True
    
    def check_lengths(self, df):
        import_headers = list(df.columns.values)
        counter = 1
        if "verbatimLocality" in import_headers:
            for vl in (df.loc[:, 'verbatimLocality']):
                counter += 1
                if len(str(vl)) > 250:
                    messages.error(self.request, "verbatimLocality is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "habitat" in import_headers:
            for hab in (df.loc[:, 'habitat']):
                counter += 1
                if len(str(hab)) > 250:
                    messages.error(self.request, "Habitat is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "samplingEffort" in import_headers:
            for se in (df.loc[:, 'samplingEffort']):
                counter += 1
                if len(str(se)) > 250:
                    messages.error(self.request, "Sampling effort is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "verbatimEventDate" in import_headers:
            for ved in (df.loc[:, 'verbatimEventDate']):
                counter += 1
                if len(str(ved)) > 250:
                    messages.error(self.request, "verbatimEventDate is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "measurementMethod" in import_headers:
            for mm in (df.loc[:, 'measurementMethod']):
                counter += 1
                if len(str(mm)) > 500:
                    messages.error(self.request, "Measurement method is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "associatedReferences" in import_headers:
            for ar in (df.loc[:, 'associatedReferences']):
                counter += 1
                if len(str(ar)) > 500:
                    messages.error(self.request, "Associated references line is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "verbatimTraitName" in import_headers:
            for vtn in (df.loc[:, 'verbatimTraitName']):
                counter += 1
                if len(str(vtn)) > 250:
                    messages.error(self.request, "verbatimTraitName is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "verbatimTraitValue" in import_headers:
            for vtv in (df.loc[:, 'verbatimTraitValue']):
                counter += 1
                if len(str(vtv)) > 250:
                    messages.error(self.request, "verbatimTraitValue is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "verbatimTraitUnit" in import_headers:
            for vtu in (df.loc[:, 'verbatimTraitUnit']):
                counter += 1
                if len(str(vtu)) > 250:
                    messages.error(self.request, "verbatimTraitUnit is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "measurementDeterminedBy" in import_headers:
            for mdb in (df.loc[:, 'measurementDeterminedBy']):
                counter += 1
                if len(str(mdb)) > 250:
                    messages.error(self.request, "measurementDeterminedBy is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "measurementRemarks" in import_headers:
            for mr in (df.loc[:, 'measurementRemarks']):
                counter += 1
                if len(str(mr)) > 250:
                    messages.error(self.request, "measurementRemarks is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "measurementAccuracy" in import_headers:
            for ma in (df.loc[:, 'measurementAccuracy']):
                counter += 1
                if len(str(ma)) > 250:
                    messages.error(self.request, "measurementAccuracy is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "statisticalMethod" in import_headers:
            for sm in (df.loc[:, 'statisticalMethod']):
                counter += 1
                if len(str(sm)) > 250:
                    messages.error(self.request, "Statistical method is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "lifeStage" in import_headers:
            for ls in (df.loc[:, 'lifeStage']):
                counter += 1
                if len(str(ls)) > 250:
                    messages.error(self.request, "lifeStage is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "verbatimLatitude" in import_headers:
            for vla in (df.loc[:, 'verbatimLatitude']):
                counter += 1
                if len(str(vla)) > 250:
                    messages.error(self.request, "verbatimLatitude is too long at row " + str(counter) + ".")
                    return False
            counter = 1
        if "verbatimLongitude" in import_headers:
            for vlo in (df.loc[:, 'verbatimLongitude']):
                counter += 1
                if len(str(vlo)) > 250:
                    messages.error(self.request, "verbatimLongitude is too long at row " + str(counter) + ".")
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
                messages.error(self.request, "There should be headerd called 'measurementValue_min' and 'measurementValue_max' or a header called 'verbatimTraitValue'.")
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
                elif value[2][0].isalpha() == True or value[2][-1].isalpha() == True:
                    if value[1] == 'nan' or pd.isnull(value[1]):
                        continue
                    elif value[2] == "nan" or pd.isnull(value[2]):
                        continue
                    else:
                        messages.error(self.request, "Mean value should be numeric at row " + str(counter) + ".")
                        return False
                else:
                    if float(value[1]) < float(value[2]):
                        messages.error(self.request, "Mean measurement value should be smaller than maximum measurement value at row " + str(counter) + ".")
                        return False
                    if float(value[0]) > float(value[2]):
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
        
def get_author(id):
    author = User.objects.filter(socialaccount__uid=id)[0]
    return author

def get_sourcereference_citation(reference, author):
    sr_old = SourceReference.objects.filter(citation__iexact=reference)
    if len(sr_old) > 0:
        return sr_old[0]
    new_reference = SourceReference(citation=reference, status=1, created_by=author)
    new_reference.save()
    response_data = get_referencedata_from_crossref(reference)
    create_masterreference(reference, response_data, new_reference, author)
    return new_reference

def get_entityclass(taxonRank, author):
    ec_all = EntityClass.objects.filter(name__iexact=taxonRank)
    if len(ec_all) > 0:
        return ec_all[0]
    new_entity = EntityClass(name=taxonRank, created_by=author)
    new_entity.save()
    return new_entity

def get_sourceentity(vs_name, reference, entity, author):
    se_old = SourceEntity.objects.filter(reference=reference, entity=entity, name__iexact=vs_name)
    if len(se_old) > 0:
        return se_old[0]
    new_sourceentity = SourceEntity(reference=reference, entity=entity, name=vs_name, created_by=author)
    new_sourceentity.save()
    create_new_entity_relation(new_sourceentity)
    return new_sourceentity

def get_timeperiod(sampling, ref, author):
    if sampling != sampling or sampling == 'nan':
        return None
    else:
        tp_all = TimePeriod.objects.filter(reference=ref, name__iexact=sampling)
        if len(tp_all) > 0:
            return tp_all[0]
        else:
            new_timeperiod = TimePeriod(reference=ref, name=sampling, created_by=author)
            new_timeperiod.save()
            return new_timeperiod

def get_sourcemethod(method, ref, author):
    if method != method or method == 'nan':
        return None
    sr_old = SourceMethod.objects.filter(reference=ref, name__iexact=method)
    if len(sr_old) > 0:
        return sr_old[0]
    else:
        new_sourcemethod = SourceMethod(reference=ref, name=method, created_by=author)
        new_sourcemethod.save()
        return new_sourcemethod

def get_sourcelocation(location, ref, author):
    if location != location or location == 'nan':
        return None
    sl_old = SourceLocation.objects.filter(name__iexact=location, reference=ref)
    if len(sl_old) > 0:
        return sl_old[0]
    else:
        new_sourcelocation = SourceLocation(reference=ref, name=location, created_by=author)
        new_sourcelocation.save()
        return new_sourcelocation

def get_choicevalue(gender):
    if gender != gender or gender == 'nan':
        return None
    if gender != '22' or gender != '23':
        return
    choicevalue = ChoiceValue.objects.filter(pk=gender)
    return choicevalue[0]


def get_fooditem_json(food):
    url = 'https://resolver.globalnames.org/name_resolvers.json?data_source_ids=3&names=' + food.lower().capitalize().replace(' ', '%20')
    try:
        file = urllib.request.urlopen(url)
        data = file.read()
        return json.loads(data)
    except:
        return {}

def create_fooditem(results, food_upper, part):
    tsn = results['data'][0]['results'][0]['taxon_id']
    taxonomic_unit = TaxonomicUnits.objects.filter(tsn=tsn)
    print(part)
    if len(taxonomic_unit)==0:
        completename = results['data'][0]['results'][0]['canonical_form']
        hierarchy_string = results['data'][0]['results'][0]['classification_path_ids'].replace('|', '-')
        hierarchy = results['data'][0]['results'][0]['classification_path'].replace('|', '-')
        kingdom = hierarchy.split('-')
        kingdom_id = Kingdom.objects.filter(name=kingdom[0])[0].pk
        path_ranks = results['data'][0]['results'][0]['classification_path_ranks'].split('|')
        rank = TaxonUnitTypes.objects.filter(rank_name=path_ranks[-1], kingdom_id=kingdom_id)[0].pk
        taxonomic_unit = TaxonomicUnits(tsn=tsn, kingdom_id=kingdom_id, rank_id=rank, completename=completename, hierarchy_string=hierarchy_string, hierarchy=hierarchy, common_names=None, tsn_update_date=None)
        taxonomic_unit.save()

    name = food_upper
    print(part)
    if part != 'nan' and part != None:
        part = ChoiceValue.objects.filter(caption=part)[0]
    else:
        part = None
    taxonomic_unit = TaxonomicUnits.objects.filter(tsn=tsn)
    food_item = FoodItem(name=name, part=part, tsn=taxonomic_unit[0], pa_tsn=taxonomic_unit[0], is_cultivar=0)
    food_item_exists = FoodItem.objects.filter(name__iexact=name)
    if len(food_item_exists) > 0:
        return food_item_exists[0]
    food_item.save()
    return food_item


def get_fooditem(food, part):
    food_upper = food.upper()
    food_item = FoodItem.objects.filter(name__iexact=food_upper)
    if len(food_item) > 0:
        return food_item[0]
    associated_taxa = re.sub('\W+', ' ', food).split(' ')
    rank_id = {}
    for item in associated_taxa:
        if len(item) < 3:
            associated_taxa.remove(item)
    if len(associated_taxa) > 1:
        for x in range(len(associated_taxa)-1):
            results = get_fooditem_json(associated_taxa[x] + ' ' + associated_taxa[x+1])
            try:
                results['data'][0]['results']
                rank = int(itis.getTaxonomicRankNameFromTSN(results['data'][0]['results'][0]['taxon_id'])['rankId'])
                rank_id[rank] = results
            except:
                pass
    if len(rank_id) == 0:
        for y in range(len(associated_taxa)):
            results = get_fooditem_json(associated_taxa[y])
        try:
            results['data'][0]['results']
            rank = int(itis.getTaxonomicRankNameFromTSN(results['data'][0]['results'][0]['taxon_id'])['rankId'])
            rank_id[rank] = results
        except:
            pass
    if len(rank_id) == 0:
        print(part)
        if part != 'nan' and part != None:
            part = ChoiceValue.objects.filter(caption=part.upper())[0]
        else:
            part = None
        food_item = FoodItem(name=food_upper, part=part, tsn=None, pa_tsn=None, is_cultivar=0)
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
    reference = get_sourcereference_citation(getattr(row, 'references'), author)
    entityclass = get_entityclass(getattr(row, 'taxonRank'), author)
    taxon =  get_sourceentity(getattr(row, 'verbatimScientificName'), reference, entityclass, author)
    if 'verbatimLocality' in headers:
        location = get_sourcelocation(getattr(row, 'verbatimLocality'), reference, author)
    else:
        location = None
    if 'sex' in headers:
        gender = get_choicevalue(getattr(row, 'sex'))
    else:
        gender = None
    if 'individualCount' in headers:
        sample_size = possible_nan_to_zero(getattr(row, 'individualCount'))
    else:
        sample_size = 0
    if 'associatedReferences' in headers:
        cited_reference =  possible_nan_to_none(getattr(row, 'associatedReferences'))
    else:
        cited_reference = None
    if 'samplingEffort' in headers:
        time_period = get_timeperiod(getattr(row, 'samplingEffort'), reference, author)
    else:
        time_period = None
    if 'measurementMethod' in headers:
        method =  get_sourcemethod(getattr(row, 'measurementMethod'), reference, author)
    else:
        method = None
    if 'verbatimEventDate' in headers:
        study_time = possible_nan_to_none(getattr(row, 'verbatimEventDate'))
    else:
        study_time = None
        
    ds_old = DietSet.objects.filter(reference=reference, taxon=taxon, location=location, gender=gender, sample_size=sample_size, cited_reference=cited_reference, time_period=time_period, method=method, study_time=study_time, created_by=author)
    if len(ds_old) > 0:
        ds = ds_old[0]
    else:
        ds = DietSet(reference=reference, taxon=taxon, location=location, gender=gender, sample_size=sample_size, cited_reference=cited_reference, time_period=time_period, method=method, study_time=study_time, created_by=author)
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
        percentage = possible_nan_to_zero(getattr(row, 'measurementValue'))
    else:
        percentage = 0
    old_ds = DietSetItem.objects.filter(diet_set=diet_set, food_item=food_item, list_order=list_order, percentage=percentage)
    if len(old_ds) == 0:
        dietsetitem = DietSetItem(diet_set=diet_set, food_item=food_item, list_order=list_order, percentage=percentage) 
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
        x = requests.get(url)
        y = x.json()
        return y
    except requests.exceptions.RequestException as e:
        print('Error: ', e)

def title_matches_citation(title, source_citation):
	# https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
    title_without_html = re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', '', title)
    title_without_space = re.sub('\s+', '', title_without_html)
    source_citation_without_html = re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', '', source_citation)
    source_citation_without_space = re.sub('\s+', '', source_citation_without_html)

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
        type = None
        x = response_data['message']['items'][0]
        fields = list()
        for field_name in x:
            fields.append(field_name)
        if 'title' not in fields:
            return False
        elif title_matches_citation(x['title'][0], source_citation) == False:
            return False
        title = re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', '', x['title'][0])
        if 'author' not in fields:
            return False
        authors = list()
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
            type = x['type']
            if type == 'journal-article':
                citation = make_harvard_citation_journalarticle(title, doi, authors, year, container_title, volume, issue, page)
            else:
                citation = ""
                for a in authors:
                    if authors.index(a) == len(authors) - 1:
                        citation += str(a)
                    else:
                        citation += str(a) + ", "
                citation += " " + str(year) + ". " + str(title) + ". Available at: " + str(doi) + "."
        
        mr = MasterReference(type=type, doi=doi, uri=uri, first_author=first_author, year=year, title=title, container_title=container_title, volume=volume, issue=issue, page=page, citation=citation, created_by=user_author)
        mr.save()
        sr.master_reference = mr
        sr.save()
        return True
        
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
    result = requests.get(url)
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
    api_result = api_query_globalnames_by_name(source_entity.name)["data"][0]
    if api_result["is_known_name"]:
        canonical_form = api_result["results"][0]["canonical_form"]
        master_entity_result = MasterEntity.objects.filter(name=canonical_form, entity_id=source_entity.entity_id,reference_id=4)
        EntityRelation(master_entity=master_entity_result[0],
                        source_entity=source_entity.id,
                        relation_id=1,
                        data_status_id=5,
                        relation_status_id=1,
                        remarks=master_entity_result[0].reference).save()

    elif api_result["results"][0]['score']>=0.75 and api_result["results"][0]['edit_distance'] <= 2:
        canonical_form = api_result["results"][0]["canonical_form"]
        master_entity_result = MasterEntity.objects.filter(name=canonical_form, entity_id=source_entity.entity_id,reference_id=4)
        if len(master_entity_result) > 0:
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
        attribute = get_sourceattribute(name, reference, entityclass, method, 2, remarks, author)
        if 'verbatimTraitValue' in headers:
            vt_value = possible_nan_to_none(getattr(row, 'verbatimTraitValue'))
        else:
            vt_value = None
        choicesetoption = get_sourcechoicesetoption(vt_value, attribute, author)
        choicesetoptionvalue = get_sourcechoicesetoptionvalue(taxon, choicesetoption, author)

    else:  
        attribute = get_sourceattribute(name, reference, entityclass, method, 1, remarks, author)
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
        create_sourcemeasurementvalue(taxon, attribute, locality, count, mes_min, mes_max, std, vt_value, statistic, unit, gender, lifestage, accuracy, measured_by, remarks, cited_reference, author)
        return

def create_sourcemeasurementvalue_no_gender(taxon, attribute, locality, count, mes_min, mes_max, std, vt_value, statistic, unit, lifestage, accuracy, measured_by, remarks, cited_reference, author):
    smv_old = SourceMeasurementValue.objects.filter(source_entity=taxon, source_attribute=attribute, source_location=locality, n_total=count, n_unknown=count, minimum=mes_min, maximum=mes_max, std=std, mean=vt_value, source_statistic=statistic, source_unit=unit, life_stage=lifestage, measurement_accuracy__iexact=accuracy, measured_by__iexact=measured_by, remarks__iexact=remarks, cited_reference__iexact=cited_reference)
    if len(smv_old) > 0:
        return
    sm_value = SourceMeasurementValue(source_entity=taxon, source_attribute=attribute, source_location=locality, n_total=count, n_unknown=count, minimum=mes_min, maximum=mes_max, std=std,  mean=vt_value, source_statistic=statistic, source_unit=unit, life_stage=lifestage, measurement_accuracy=accuracy, measured_by=measured_by, remarks=remarks, cited_reference=cited_reference, created_by=author)
    sm_value.save()

def create_sourcemeasurementvalue(taxon, attribute, locality, count, mes_min, mes_max, std, vt_value, statistic, unit, gender, lifestage, accuracy, measured_by, remarks, cited_reference, author):
    n_female = 0
    n_male = 0
    n_unknown = 0
    if isinstance(gender, type(None)):
        create_sourcemeasurementvalue_no_gender(taxon, attribute, locality, count, mes_min, mes_max, std, vt_value, statistic, unit, lifestage, accuracy, measured_by, remarks, cited_reference, author)
        return 
    elif gender.caption.lower() == 'female':
        n_female = count
    elif gender.caption.lower() == 'male':
        n_male = count
    else:
        n_unknown = count     
    smv_old = SourceMeasurementValue.objects.filter(source_entity=taxon, source_attribute=attribute, source_location=locality, n_total=count, n_female=n_female, n_male=n_male, n_unknown=n_unknown, minimum=mes_min, maximum=mes_max, std=std, mean=vt_value, source_statistic=statistic, source_unit=unit, gender=gender, life_stage=lifestage, measurement_accuracy__iexact=accuracy, measured_by__iexact=measured_by, remarks__iexact=remarks, cited_reference__iexact=cited_reference)
    if len(smv_old) > 0:
        return
    sm_value = SourceMeasurementValue(source_entity=taxon, source_attribute=attribute, source_location=locality, n_total=count, n_female=n_female, n_male=n_male, n_unknown=n_unknown, minimum=mes_min, maximum=mes_max, std=std,  mean=vt_value, source_statistic=statistic, source_unit=unit, gender=gender, life_stage=lifestage, measurement_accuracy=accuracy, measured_by=measured_by, remarks=remarks, cited_reference=cited_reference, created_by=author)
    sm_value.save()
    return

def get_choicevalue_ets(choice, set, author):
    if choice != choice or choice == 'nan':
        return None
    choiceset = ChoiceValue.objects.filter(caption__iexact=choice, choice_set__iexact=set)
    if len(choiceset) > 0:
        return choiceset[0]
    cv = ChoiceValue.objects.create(caption=choice, choice_set=set, created_by=author)
    return cv

def get_sourceunit(unit, author):
    if unit != unit or unit == 'nan':
        return None
    su_old = SourceUnit.objects.filter(name__iexact=unit)
    if len(su_old) > 0:
        return su_old[0]
    su = SourceUnit(name=unit, created_by=author)
    su.save()
    return su

def get_sourcechoicesetoptionvalue(entity, sourcechoiceoption, author):
    scov_old = SourceChoiceSetOptionValue.objects.filter(source_entity=entity, source_choiceset_option=sourcechoiceoption)
    if len(scov_old) > 0:
        return scov_old[0]
    scov = SourceChoiceSetOptionValue(source_entity=entity, source_choiceset_option=sourcechoiceoption, created_by=author)
    scov.save()
    return scov

def get_sourcechoicesetoption(name, attribute, author):
    if name == 'nan' or name == 'NA' or name != name:
        return None
    sco_old = SourceChoiceSetOption.objects.filter(source_attribute=attribute, name__iexact=name)
    if len(sco_old) > 0:
        return sco_old[0]
    sco = SourceChoiceSetOption(source_attribute=attribute, name=name, created_by=author)
    sco.save()
    return sco

def get_sourcestatistic(statistic, ref, author):
    if statistic != statistic or statistic == 'nan':
        return None
    ss_old = SourceStatistic.objects.filter(name__iexact=statistic, reference=ref)
    if len(ss_old) > 0:
        return ss_old[0]
    ss = SourceStatistic(name=statistic, reference=ref, created_by=author)
    ss.save()
    return ss

def get_sourceattribute(name, ref, entity, method, type_value, remarks, author):
    sa_old = SourceAttribute.objects.filter(name__iexact=name, reference=ref, entity=entity, method=method, type=type_value, remarks=remarks)
    if len(sa_old) > 0:
        return sa_old[0]
    sa = SourceAttribute(name=name, reference=ref, entity=entity, method=method, type=type_value, remarks=remarks, created_by=author)
    sa.save()
    return sa
