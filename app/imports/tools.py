from mb.models import ChoiceValue, DietSet, EntityClass, SourceEntity, SourceLocation, SourceMethod, SourceReference, TimePeriod, DietSetItem, FoodItem
from django.contrib import messages
from django.db import transaction

import pandas as pd
import re
import json
import urllib.request
import requests

class Check:
    def __init__(self, request):
        self.request = request

    def check_all(self, df):

        if self.check_headers(df) == False:
            return False
        if self.check_author(df) == False:
            return False
        if self.check_verbatimScientificName(df) == False:
            return False
        if self.check_taxonRank(df) == False:
            return False
        if self.check_sequence(df) == False:
            return False
        if self.check_measurementValue(df) == False:
            return False
        if self.check_references(df) == False:
            return False
        return True

    def check_headers(self, df):
        import_headers = list(df.columns.values)
        accepted_headers = ['author', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence',  'references']

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
        for name in pd.isnull(df.loc[:, 'verbatimScientificName']):
            counter += 1
            if name == True:
                messages.error(self.request, "Scientific name is empty on the line " + str(counter) + ".")
                return False

        counter = 1
        for name in (df.loc[:, 'verbatimScientificName']):
            counter += 1
            names_list = name.split()
            if len(names_list) > 3:
                messages.error(self.request, "Scientific name is not in the correct form on the line " + str(counter) + ".")
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

    def check_sequence(self, df):
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
                        if 'individuaCount' in df.columns.values:
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
                        if 'individuaCount' in df.columns.values:
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
                            continue
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
                continue
            else:
                messages.error(self.request, "The measurement value on the line " + str(counter) + " is not a number.")
                return False
        return True

    def check_references(self, df):
        counter = 1
        for ref in (df.loc[:, 'references']):
            if len(ref) < 10 or len(ref) > 500:
                messages.error(self.request, "Reference is too short or too long on the line " + str(counter) + ".")
                return False
            match = re.match(r'.*([1-2][0-9]{3})', ref)
            counter += 1
            if match is None:
                messages.error(self.request, "Reference does not have a year number on the line " + str(counter) + ".")
                return False

        return True

def get_sourcereference_citation(reference):
    sr = SourceReference.objects.filter(citation__iexact=reference)
    if len(sr) > 0:
        return sr[0]
    else:
        new_reference = SourceReference(citation=reference, status=1)
        new_reference.save()
        return new_reference

def get_entityclass(taxonRank):
    ec = EntityClass.objects.filter(name__iexact=taxonRank)
    if len(ec) > 0:
        return(ec[0])
    else:
        new_entity = EntityClass(name=taxonRank)
        new_entity.save()
        return new_entity

def get_sourceentity(vs_name, reference, entity):
    se = SourceEntity.objects.filter(name__iexact=vs_name)
    if len(se) > 0:
        return se[0]
    else:
        new_sourceentity = SourceEntity(reference=reference, entity=entity, name=vs_name)
        new_sourceentity.save()
        return new_sourceentity

def get_timeperiod(sampling, ref):
    if sampling != sampling:
        return None
    tp = TimePeriod.objects.filter(name__iexact=sampling)
    if len(tp) > 0:
        return tp[0]
    else:
        new_timeperiod = TimePeriod(reference=ref, name=sampling)
        new_timeperiod.save()
        return new_timeperiod

def get_sourcemethod(method, ref):
    if method != method:
        return None
    sm = SourceMethod.objects.filter(name__iexact=method)
    if len(sm) > 0:
        return sm[0]
    else:
        new_sourcemethod = SourceMethod(reference=ref, name=method)
        new_sourcemethod.save()
        return new_sourcemethod

def get_sourcelocation(location, ref):
    if location != location:
        return None
    sl = SourceLocation.objects.filter(name__iexact=location)
    if len(sl) > 0:
        return sl[0]
    else:
        new_sourcelocation = SourceLocation(reference=ref, name=location)
        new_sourcelocation.save()
        return new_sourcelocation
 
def get_choicevalue(gender):
    if gender != gender:
        return None
    if gender != '22' or gender != '23':
        return
    choicevalue = ChoiceValue.objects.filter(pk=gender)
    return choicevalue[0]

def possible_nan_to_zero(size):
    if size != size:
        return 0
    return size

def possible_nan_to_none(possible):
    if possible != possible:
        return None
    return possible

@transaction.atomic
def create_dietset(row):
    reference = get_sourcereference_citation(getattr(row, 'references'))
    entityclass = get_entityclass(getattr(row, 'taxonRank'))
    taxon =  get_sourceentity(getattr(row, 'verbatimScientificName'), reference, entityclass)
    location = get_sourcelocation(getattr(row, 'verbatimLocality'), reference)
    gender = get_choicevalue(getattr(row, 'sex'))
    sample_size = possible_nan_to_zero(getattr(row, 'individualCount'))
    cited_reference =  possible_nan_to_none(getattr(row, 'associatedReferences'))
    time_period = get_timeperiod(getattr(row, 'samplingEffort'), reference)
    method =  get_sourcemethod(getattr(row, 'measurementMethod'), reference)
    study_time = possible_nan_to_none(getattr(row, 'verbatimEventDate'))
    
    if (getattr(row, 'sequence') == 1):
        ds_all = DietSet.objects.filter(reference=reference, taxon=taxon, location=location, gender=gender, sample_size=sample_size, cited_reference=cited_reference, time_period=time_period, method=method, study_time=study_time)
        if len(ds_all) == 0:
            ds = DietSet(reference=reference, taxon=taxon, location=location, gender=gender, sample_size=sample_size, cited_reference=cited_reference, time_period=time_period, method=method, study_time=study_time)
            ds.save()

def trim(text:str):
    return " ".join(text.split())

def trim_df(df):
    headers = df.columns
    for i, row in df.iterrows():
        for header in headers:
            df.at[i, header] = trim(str(df.at[i, header]))
