from mb.models import SourceReference
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
    if len(sr)>0:
        return sr[0]
    else:
        new_reference = SourceReference(citation=reference['references'], status=1)
        new_reference.save()
        return new_reference
