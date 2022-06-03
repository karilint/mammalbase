from weakref import ref
from mb.models import ChoiceValue, EntityClass, SourceEntity, SourceLocation, SourceMethod, SourceReference, TimePeriod
from django.contrib import messages
import pandas as pd

def check_all(request, df):
    if check_headers(df) == False:
        messages.error(request, "The import file does not contain the required headers.")
        return False
    if check_author(df) == False:
        messages.error(request, "Not all the authors were in the correct form.")
        return False
    if check_verbatimScientificName(df) == False:
        messages.error(request, "Not all the scientific names were in the correct form.")
        return False
    if check_taxonRank(df) == False:
        messages.error(request, "Not all the taxonomic ranks were in the correct form.")
        return False
    if check_sequence(df) == False:
        messages.error(request, "Not everything was correct with sequencing.")
        return False
    if check_measurementValue(df) == False:
        messages.error(request, "Not all the measurement values were numbers.")
        return False
    return True

def check_headers(df):
    import_headers = list(df.columns.values)
    accepted_headers = ['author', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence',  'references']

    for header in accepted_headers:
        if header not in import_headers:
            return False
    return True

def check_author(df):
    numbers = []
    for author in (df.loc[:, 'author']):
        if len(str(author)) != 19:
            return False
        numbers.append(author.replace("-", ""))
    
    for number in numbers:
        if not number.isdigit():
            return False
    return True

def check_verbatimScientificName(df):
    for name in pd.isnull(df.loc[:, 'verbatimScientificName']):
        if name == True:
            return False

    for name in (df.loc[:, 'verbatimScientificName']):
        names_list = name.split()
        if len(names_list) > 3:
            return False
    return True

def check_taxonRank(df):
    for rank in (df.loc[:, 'taxonRank']):
        if rank not in ['Genus', 'Species', 'Subspecies', 'genus', 'species', 'subspecies']:
            return False
    return True

def check_sequence(df):
    df_new = df[['verbatimScientificName', 'verbatimAssociatedTaxa', 'sequence', 'references']]
    counter = 0
    total = 1
    fooditems = []

    for item in df_new.values:
        if item[2] == counter:
            if item[0] != scientific_name or item[3] != references or item[1] in fooditems:
                return False
            fooditems.append(item[1])
            counter += 1
            total += item[2]
        else:
            counter -= 1
            sum = (counter*(counter+1))/2
            if counter != -1 and sum != total:
                return False
            total = 1
            counter = 2
            scientific_name = item[0]
            references = item[3]
            fooditems = [item[1]]
    return True

def check_measurementValue(df):
    import_headers = list(df.columns.values)
    if "measurementValue" not in import_headers:
        return True
    
    for value in (df.loc[:, 'measurementValue']):
        if pd.isnull(value) == True or any(c.isalpha() for c in str(value)) == False:
            continue
        else:
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

