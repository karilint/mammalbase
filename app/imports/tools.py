from doctest import master
from mb.models import ChoiceValue, DietSet, EntityClass, MasterReference, SourceEntity, SourceLocation, SourceMethod, SourceReference, TimePeriod, DietSetItem, FoodItem
from itis.models import TaxonomicUnits, Kingdom, TaxonUnitTypes
from django.contrib import messages
from django.db import transaction
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User

import pandas as pd
import re
import json
import urllib.request
import requests
import time

class Check:
    def __init__(self, request):
        self.request = request
        self.id = None

    def check_all(self, df):
        if self.check_headers(df) == False:
            return False
        elif self.check_author(df) == False:
            return False
        elif self.check_verbatimScientificName(df) == False:
            return False
        elif self.check_taxonRank(df) == False:
            return False
        elif self.check_sequence(df) == False:
            return False
        elif self.check_measurementValue(df) == False:
            return False
        elif self.check_references(df) == False:
            return False
        return True

    def check_valid_author(self, df):
        for author in (df.loc[:, 'author']):
            data = SocialAccount.objects.all().filter(uid=author)
            if data.exists() == False:
                messages.error(self.request, "The author " + str(author) + " is not a valid ORCID ID.")
                return False
            self.id = data[0].user_id
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

        df_new = df[['verbatimScientificName', 'taxonRank']]
        counter = 1
        for item in df_new.values:
            counter += 1
            names_list = item[0].split()
            if len(names_list) > 3:
                messages.error(self.request, "Scientific name is not in the correct format on the line " + str(counter) + ".")
                return False
            if len(names_list) == 3 and item[1] not in ['Subspecies', 'subspecies']:
                messages.error(self.request, "Scientific name is not in the correct format or taxonomic rank should be 'Subspecies' on the line " + str(counter) + ".")
                return False
            if len(names_list) == 2 and item[1] not in ['Species', 'species']:
                messages.error(self.request, "Scientific name is not in the correct format or taxonomic rank should be 'Species' on the line " + str(counter) + ".")
                return False
            if len(names_list) == 1 and item[1] not in ['Genus', 'genus']:
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


def get_author(id):
    author = User.objects.filter(socialaccount__uid=id)[0]
    return author

def get_sourcereference_citation(reference, author):
    sr_old = SourceReference.objects.filter(citation__iexact=reference)
    if len(sr_old) > 0:
        if sr_old[0].master_reference == None:
            response_data = get_referencedata_from_crossref(reference) # Voi kommentoida pois testeissä, hidastaa testejä..
            create_masterreference(reference, response_data, sr_old[0], author) # Voi kommentoida pois testeissä, hidastaa testejä..
            return sr_old[0]
        return sr_old[0]
    new_reference = SourceReference(citation=reference, status=1, created_by=author)
    new_reference.save()
    response_data = get_referencedata_from_crossref(reference) # Voi kommentoida pois testeissä, hidastaa testejä..
    create_masterreference(reference, response_data, new_reference, author) # Voi kommentoida pois testeissä, hidastaa testejä..
    return new_reference

def get_entityclass(taxonRank, author):
    ec_all = EntityClass.objects.filter(name__iexact=taxonRank)
    if len(ec_all) > 0:
        return ec_all[0]
    new_entity = EntityClass(name=taxonRank, created_by=author)
    new_entity.save()
    return new_entity

def get_sourceentity(vs_name, reference, entity, author):
    se_old = SourceEntity.objects.filter(reference=reference, entity=entity, name=vs_name)
    if len(se_old) > 0:
        return se_old[0]
    new_sourceentity = SourceEntity(reference=reference, entity=entity, name=vs_name, created_by=author)
    new_sourceentity.save()
    return new_sourceentity

def get_timeperiod(sampling, ref, author):
    if sampling != sampling:
        return None
    else:
        tp_all = TimePeriod.objects.filter(reference=ref, name=sampling)
        if len(tp_all) > 0:
            return tp_all[0]
        else:
            new_timeperiod = TimePeriod(reference=ref, name=sampling, created_by=author)
            new_timeperiod.save()
            return new_timeperiod

def get_sourcemethod(method, ref, author):
    if method != method:
        return None
    sr_old = SourceMethod.objects.filter(reference=ref, name=method)
    if len(sr_old) > 0:
        return sr_old[0]
    else:
        new_sourcemethod = SourceMethod(reference=ref, name=method, created_by=author)
        new_sourcemethod.save()
        return new_sourcemethod

def get_sourcelocation(location, ref, author):
    if location != location:
        return None
    sl_old = SourceLocation.objects.filter(name=location, reference=ref)
    if len(sl_old) > 0:
        return sl_old[0]
    else:
        new_sourcelocation = SourceLocation(reference=ref, name=location, created_by=author)
        new_sourcelocation.save()
        return new_sourcelocation

def get_choicevalue(gender):
    if gender != gender:
        return None
    if gender != '22' or gender != '23':
        return
    choicevalue = ChoiceValue.objects.filter(pk=gender)
    return choicevalue[0]


def get_fooditem(food):
    food_upper = food.upper()
    food_item = FoodItem.objects.filter(name__iexact=food_upper)
    if len(food_item) > 0:
        return food_item[0]

    def get_json(food):
        url = 'https://resolver.globalnames.org/name_resolvers.json?data_source_ids=3&names=' + food.lower().capitalize().replace(' ', '%20')
        file = urllib.request.urlopen(url)
        data = file.read()
        return json.loads(data)

    def create_fooditem(results):
        tsn = results['data'][0]['results'][0]['taxon_id']
        taxonomic_unit = TaxonomicUnits.objects.filter(tsn=tsn)

        if len(taxonomic_unit)==0:
            completename = results['data'][0]['results'][0]['canonical_form']
            hierarchy_string = results['data'][0]['results'][0]['classification_path_ids'].replace('|', '-')
            hierarchy = results['data'][0]['results'][0]['classification_path'].replace('|', '-')
            common_names = None
            kingdom = hierarchy.split('-')
            kingdom_id = Kingdom.objects.filter(name=kingdom[0])[0].pk
            path_ranks = results['data'][0]['results'][0]['classification_path_ranks'].split('|')
            rank = TaxonUnitTypes.objects.filter(rank_name=path_ranks[-1], kingdom_id=kingdom_id)[0].pk
            tsn_update_date = None
            taxonomic_unit = TaxonomicUnits(tsn=tsn, kingdom_id=kingdom_id, rank_id=rank, completename=completename, hierarchy_string=hierarchy_string, hierarchy=hierarchy, common_names=common_names, tsn_update_date=tsn_update_date)
            taxonomic_unit.save()

        name = food_upper
        part = ChoiceValue.objects.filter(pk=21)[0]
        is_cultivar = 0
        taxonomic_unit = TaxonomicUnits.objects.filter(tsn=tsn)
        food_item = FoodItem(name=name, part=part, tsn=taxonomic_unit[0], pa_tsn=taxonomic_unit[0], is_cultivar=is_cultivar)
        food_item_exists = FoodItem.objects.filter(name__iexact=name)
        if len(food_item_exists) > 0:
            return food_item_exists[0]
        food_item.save()
        return food_item
    foods = get_json(food_upper) 
    try:
        foods['data'][0]['results']
        return create_fooditem(foods)

    except KeyError:
        new = food_upper.split('(', 1)[0]
        food_item = FoodItem.objects.filter(name__iexact=new)
        if len(food_item) > 0:
            return food_item[0]
        new_food = get_json(new) 
        try:
            new_food['data'][0]['results']
            return create_fooditem(new_food)
        except KeyError:
            food_item = FoodItem.objects.filter(name__iexact=food_upper)
            if len(food_item) > 0:
                return food_item[0]
            empty_food_item = FoodItem(name=food_upper, part=None, tsn=None, pa_tsn=None, is_cultivar=0)
            empty_food_item.save()
            return empty_food_item

def possible_nan_to_zero(size):
    if size != size:
        return 0
    return size

def possible_nan_to_none(possible):
    if possible != possible:
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
    if 'verbatimEventdate' in headers:
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

def create_dietsetitem(row, diet_set, headers):
    food_item = get_fooditem(getattr(row, 'verbatimAssociatedTaxa'))
    list_order = getattr(row, 'sequence')
    if 'measurementValue' in headers:
        percentage = possible_nan_to_zero(getattr(row, 'measurementValue'))
    else:
        percentage = 0
    ds = DietSet.objects.filter(taxon=diet_set.taxon, reference=diet_set.reference)[0]
    dietsetitem = DietSetItem(diet_set=ds, food_item=food_item, list_order=list_order, percentage=percentage)
    old_ds = DietSetItem.objects.filter(diet_set=ds, food_item=food_item)
    if len(old_ds) == 0:
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
    url = 'https://api.crossref.org/works?query.bibliographic=%22'+c+'%22&mailto=mammalbase@gmail.com&rows=2'
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