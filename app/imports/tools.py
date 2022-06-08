from mb.models import ChoiceValue, DietSet, EntityClass, SourceEntity, SourceLocation, SourceMethod, SourceReference, TimePeriod
from django.contrib import messages
from django.db import transaction

import pandas as pd
import re

def check_all(request, df):
    if check_headers(df, request) == False:
        return False
    if check_author(df, request) == False:
        return False
    if check_verbatimScientificName(df, request) == False:
        return False
    if check_taxonRank(df, request) == False:
        return False
    if check_sequence(df, request) == False:
        return False
    if check_measurementValue(df, request) == False:
        return False
    if check_references(df, request) == False:
        return False
    return True

def check_headers(df, request):
    import_headers = list(df.columns.values)
    accepted_headers = ['author', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence',  'references']

    for header in accepted_headers:
        if header not in import_headers:
            messages.error(request, "The import file does not contain the required headers. The missing header is: " + str(header) + ".")
            return False
    return True

def check_author(df, request):
    numbers = []
    counter = 1
    for author in (df.loc[:, 'author']):
        counter += 1
        if len(str(author)) != 19:
            messages.error(request, "The author on the line number " + str(counter) + " is not in the correct form.")
            return False
        numbers.append(author.replace("-", ""))
    
    counter = 1
    for number in numbers:
        counter += 1
        if not number.isdigit():
            messages.error(request, "The author on the line number " + str(counter) + " is not in the correct form.")
            return False
    return True

def check_verbatimScientificName(df, request):
    counter = 1
    for name in pd.isnull(df.loc[:, 'verbatimScientificName']):
        counter += 1
        if name == True:
            messages.error(request, "Scientific name is empty on the line " + str(counter) + ".")
            return False

    counter = 1
    for name in (df.loc[:, 'verbatimScientificName']):
        counter += 1
        names_list = name.split()
        if len(names_list) > 3:
            messages.error(request, "Scientific name is not in the correct form on the line " + str(counter) + ".")
            return False
    return True

def check_taxonRank(df, request):
    counter = 1
    for rank in (df.loc[:, 'taxonRank']):
        counter += 1
        if rank not in ['Genus', 'Species', 'Subspecies', 'genus', 'species', 'subspecies']:
            messages.error(request, "Taxonomic rank is not in the correct form on the line " + str(counter) + ".")
            return False
    return True

def check_sequence(df, request):
    df_new = df[['verbatimScientificName', 'verbatimAssociatedTaxa', 'sequence', 'references']]
    counter = 0
    total = 1
    fooditems = []
    lines = 1
    for item in df_new.values:
        lines += 1
        if str(item[2]).isnumeric():            
            if int(item[2]) == counter:
                if item[0] != scientific_name:
                    messages.error(request, "Scientific name on the line " + str(lines) + " should be '" + str(scientific_name) + "'.")
                    return False
                if item[3] != references:
                    messages.error(request, "References on the line " + str(lines) + " should be '" + str(references) + "'.")
                    return False
                if item[1] in fooditems:
                    messages.error(request, "Food item on the line " + str(lines) + " is already mentioned for this diet set.")
                    return False
                fooditems.append(item[1])
                counter += 1
                total += int(item[2])

            else:
                if int(item[2]) == 1:
                    total = 1
                    counter = 2
                    scientific_name = item[0]
                    references = item[3]
                    fooditems = [item[1]]
                    continue
                else:
                    sum = (counter*(counter+1))/2
                    counter -= 1
                    if counter != -1 and sum != total:
                        messages.error(request, "Check the sequence numbering on the line " + str(lines) + ".")
                        return False

        else:
            messages.error(request, "Sequence number on the line " + str(lines) + " is not numeric.")
            return False
        
    return True

def check_measurementValue(df, request):
    import_headers = list(df.columns.values)
    if "measurementValue" not in import_headers:
        return True
    
    counter = 1
    for value in (df.loc[:, 'measurementValue']):
        counter += 1
        if pd.isnull(value) == True or any(c.isalpha() for c in str(value)) == False:
            continue
        else:
            messages.error(request, "The measurement value on the line " + str(counter) + " is not a number.")
            return False
    return True

def check_references(df, request):
    counter = 1
    for ref in (df.loc[:, 'references']):
        match = re.match(r'.*([1-2][0-9]{3})', ref)
        counter += 1
        if match is None:
            messages.error(request, "Reference does not have a year number on the line " + str(counter) + ".")
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
	# gender =
    sample_size = possible_nan_to_zero(getattr(row, 'individualCount'))
    cited_reference =  possible_nan_to_none(getattr(row, 'associatedReferences'))
    time_period = get_timeperiod(getattr(row, 'samplingEffort'), reference)
    method =  get_sourcemethod(getattr(row, 'measurementMethod'), reference)
    study_time = possible_nan_to_none(getattr(row, 'verbatimEventDate'))

    ds = DietSet(reference=reference, taxon=taxon, location=location, sample_size=sample_size, cited_reference=cited_reference, time_period=time_period, method=method, study_time=study_time)
    ds.save()

def trim(text:str):
    return " ".join(text.split())

def trim_df(df):
    headers = df.columns
    for i, row in df.iterrows():
        for header in headers:
            df.at[i, header] = trim(str(df.at[i, header]))
