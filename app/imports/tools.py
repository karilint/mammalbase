from mb.models import ChoiceValue, EntityClass, SourceEntity, SourceLocation, SourceMethod, SourceReference, TimePeriod
import pandas as pd

def check_all(df):
    if check_headers(df) == True and check_taxonRank(df) == True and check_author(df) == True and check_verbatimScientificName(df) == True:
        return True

def check_headers(df):
    import_headers = list(df.columns.values)
    accepted_headers = ['author', 'verbatimScientificName', 'taxonRank', 'verbatimLocality', 'sex', 'individualCount', 'measurementMethod', 'associatedReferences', 'references']

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
    tp = TimePeriod.objects.filter(name__iexact=sampling)
    if len(tp) > 0:
        return tp[0]
    else:
        new_timeperiod = TimePeriod(reference=ref, name=sampling)
        new_timeperiod.save()
        return new_timeperiod

def get_sourcemethod(method, ref):
    sm = SourceMethod.objects.filter(name__iexact=method)
    if len(sm) > 0:
        return sm[0]
    else:
        new_sourcemethod = SourceMethod(reference=ref, name=method)
        new_sourcemethod.save()
        return new_sourcemethod

def get_sourcelocation(location, ref):
    sl = SourceLocation.objects.filter(name__iexact=location)
    if len(sl) > 0:
        return sl[0]
    else:
        new_sourcelocation = SourceLocation(reference=ref, name=location)
        new_sourcelocation.save()
        return new_sourcelocation

