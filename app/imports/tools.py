from doctest import master
from mb.models import ChoiceValue, DietSet, EntityClass, MasterReference, SourceEntity, SourceLocation, SourceMethod, SourceReference, TimePeriod, DietSetItem, FoodItem
from itis.models import TaxonomicUnits, Kingdom, TaxonUnitTypes
from django.contrib import messages
from django.db import transaction
from allauth.socialaccount.models import SocialAccount

import pandas as pd
import re
import json
import urllib.request
import requests
import time
import logging

class Check:
    def __init__(self, request):
        self.request = request

    def check_all(self, df):
        # if self.check_valid_author(df) == False: #Testi menee vikaan
        #     return False
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

    def check_valid_author(self, df):
        for author in (df.loc[:, 'author']):
            if SocialAccount.objects.all().filter(uid=author).exists() == False:
                messages.error(self.request, "The author " + str(author) + " is not a valid ORCID ID.")
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
                pass
            else:
                messages.error(self.request, "The measurement value on the line " + str(counter) + " is not a number.")
                return False
            if value <= 0:
                messages.error(self.request, "The measurement value on the line " + str(counter) + " nneds to be bigger than zero.")
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
    sr_old = SourceReference.objects.filter(citation__iexact=reference)
    if len(sr_old) > 0:
        return sr_old[0]
    new_reference = SourceReference(citation=reference, status=1)
    new_reference.save()
    #response_data = get_referencedata_from_crossref(reference)
    #create_masterreference(reference, response_data, new_reference)
    return new_reference

def get_entityclass(taxonRank):
    ec_all = EntityClass.objects.filter(name__iexact=taxonRank)
    if len(ec_all) > 0:
        return ec_all[0]
    new_entity = EntityClass(name=taxonRank)
    new_entity.save()
    return new_entity

def get_sourceentity(vs_name, reference, entity):
    se_old = SourceEntity.objects.filter(reference=reference, entity=entity, name=vs_name)
    if len(se_old) > 0:
        return se_old[0]
    new_sourceentity = SourceEntity(reference=reference, entity=entity, name=vs_name)
    new_sourceentity.save()
    return new_sourceentity

def get_timeperiod(sampling, ref):
    if sampling != sampling:
        return None
    else:
        tp_all = TimePeriod.objects.filter(reference=ref, name=sampling)
        if len(tp_all) > 0:
            return tp_all[0]
        else:
            new_timeperiod = TimePeriod(reference=ref, name=sampling)
            new_timeperiod.save()
            return new_timeperiod

def get_sourcemethod(method, ref):
    if method != method:
        return None
    sr_old = SourceMethod.objects.filter(reference=ref, name=method)
    if len(sr_old) > 0:
        return sr_old[0]
    else:
        new_sourcemethod = SourceMethod(reference=ref, name=method)
        new_sourcemethod.save()
        return new_sourcemethod

def get_sourcelocation(location, ref):
    if location != location:
        return None
    sl_old = SourceLocation.objects.filter(name=location, reference=ref)
    if len(sl_old) > 0:
        return sl_old[0]
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

        ds = DietSet(reference=reference, taxon=taxon, location=location, gender=gender, sample_size=sample_size, cited_reference=cited_reference, time_period=time_period, method=method, study_time=study_time)
        if (getattr(row, 'sequence') == 1):
            ds.save()
        
def trim(text:str):
    return " ".join(text.split())

def trim_df(df):
    headers = df.columns
    for i, row in df.iterrows():
        for header in headers:
            df.at[i, header] = trim(str(df.at[i, header]))

# Search citation from CrossrefApi: https://api.crossref.org/swagger-ui/index.htm
# Please do not make any unnessecary queries: https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/
def get_referencedata_from_crossref(citation):
	c = citation.replace(" ", "%20")
	url = 'https://api.crossref.org/works?query.bibliographic=%22'+c+'%22&mailto=mammalbase@gmail.com&rows=2'
	try:
		x = requests.get(url)
		y = x.json()
		return y
	except requests.exceptions.RequestException as e:
		print('Error: ', e)

# Check if SourceReference.citation matching MasterReference exists
def get_masterreference(citation):
	sr_all = SourceReference.objects.filter(citation__iexact=citation, status=1, master_reference=None)
	if len(sr_all) > 0:
		return False
	return True

def title_matches_citation(title, source_citation):
	# https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
    title_without_html = re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', '', title)
    if title_without_html.lower() not in source_citation.lower():
        print('Title ', title_without_html , ' is not in citation')
        return False
    return True

def create_masterreference(source_citation, response_data, sr):
    if get_masterreference == True:
        return False
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
                citation = str(first_author) + '. ' + str(title) + '. Available at: ' + str(doi)
        
        mr = MasterReference(type=type, doi=doi, uri=uri, first_author=first_author, year=year, title=title, container_title=container_title, volume=volume, issue=issue, page=page, citation=citation)
        mr.save()
        sr.master_reference = mr
        sr.save()
        return True
        
    except Exception as e:
        print('Error: ', e)
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