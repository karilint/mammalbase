import re
from django.db import transaction
import pandas as pd
import requests
from mb.models.models import SourceReference, MasterReference, EntityClass, SourceEntity, EntityRelation, MasterEntity, TimePeriod, SourceMethod, ChoiceValue
from mb.models.location_models import SourceLocation
from datetime import timedelta
from config.settings import ITIS_CACHE
from requests_cache import CachedSession
import itis.views as itis
import json
from django.contrib.auth.models import User
import logging
from itis.models import TaxonomicUnits
from itis.views import *
from itis.models import TaxonomicUnits, Kingdom, TaxonUnitTypes
from decimal import Decimal
from django.contrib import messages

class BaseImporter:
    """
    Base class for all importers
    """

    @transaction.atomic
    def importRow(self, row : pd.Series):
        pass

    def make_harvard_citation_journalarticle(title, d, authors, year, container_title, volume, issue, page):
        citation = ""
        for a in authors:
            if authors.index(a) == len(authors) - 1:
                citation += str(a)
            else:
                citation += str(a) + ", "
        
        citation += " " + str(year) + ". " + str(title) + ". " + str(container_title) + ". " + str(volume) + "(" + str(issue) + "), pp." + str(page) + ". Available at: " + str(d) + "." 
        return citation
    
    def get_author(self, social_id: str):
        """
        Return User object for the given social_id
        """
        author = User.objects.filter(socialaccount__uid=social_id)
        if author.count() == 1:
            return author[0]
        else:
            raise Exception("Author not found")
        
    def get_master_reference_from_cross_ref(self, citation: str, user_author: User):
        """
        Gets the master reference from crossref API
        https://api.crossref.org/swagger-ui/index.htm
        """
        formatted_citation = citation.replace(" ", "%20")
        url = f'https://api.crossref.org/works?query.bibliographic="{formatted_citation}"&mailto=kari.lintulaakso@helsinki.fi&rows=2'
        try:
            response = requests.get(url, timeout=300).json()
            items = response.get('message', {}).get('items', [])
            if not items:
                return False

            # Process the first item
            item = items[0]
            title = re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', '', item.get('title', [''])[0])
            authors = [f"{a['family']}, {a['given'][0]}." for a in item.get('author', [])]
            first_author = authors[0] if authors else ""
            doi = item.get('DOI', '')
            uri = item.get('uri', '')
            year = item.get('published', {}).get('date-parts', [[None]])[0][0]
            container_title = item.get('container-title', [''])[0]
            volume = item.get('volume', None)
            issue = item.get('issue', '')
            page = item.get('page', '')
            ref_type = item.get('type', '')

            # Create citation based on type
            if ref_type == 'journal-article':
                citation = self.make_harvard_citation_journalarticle(title, doi, authors, year, container_title, volume, issue, page)
            else:
                authors_str = ", ".join(authors)
                citation = f"{authors_str} {year}. {title}. Available at: {doi}."

            # Create and save MasterReference
            mr = MasterReference(
                type=ref_type, doi=doi, uri=uri, first_author=first_author, year=year,
                title=title, container_title=container_title, volume=volume, issue=issue,
                page=page, citation=citation, created_by=user_author
            )
            mr.save()
            return mr

        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_or_create_master_reference(self, citation: str, author: User):
        """
        Return MasterReference object for the given source_reference
        """
        master_reference = MasterReference.objects.filter(citation=citation)
        if master_reference.count() == 1:
            return master_reference[0]
        else:
            new_master_reference = self.get_master_reference_from_cross_ref(citation, author)
            if new_master_reference:                                                                                                                          
                return new_master_reference
            else:
                return None
    
    def get_or_create_source_reference(self, citation: str, author: User):
        """
        Return new or exists source reference.
        """
        if (citation.lower() == "nan" or citation == None) or (str(author).lower() == "nan" or author == None):
            raise Exception("SourceReference is not valid!")

        source_reference = SourceReference.objects.filter(citation__iexact=citation)
        
        if source_reference.count() == 1:
            return source_reference[0]
        
        
        new_reference = SourceReference(citation=citation,status=1, created_by=author)
        master_reference = self.get_or_create_master_reference(citation, author)
        new_reference.master_reference = master_reference
        new_reference.save()

        return new_reference
        
    def get_or_create_entity_class(self, taxon_rank: str, author: User):
        """
        Return EntityClass object for the given taxon_rank or create a new one
        """
        entity_class = EntityClass.objects.filter(name__iexact=taxon_rank)
        if entity_class.count() == 1:
            return entity_class[0]
        else:
            new_entity_class = EntityClass(name=taxon_rank, created_by=author)
            new_entity_class.save()
            return new_entity_class
    
    def get_or_create_source_entity(self, name: str, source_reference: SourceReference, entity_class: EntityClass, author: User):
        """
        Return SourceEntity object for the given name or create a new one
        """
        source_entity = SourceEntity.objects.filter(name__iexact=name, reference=source_reference)
        if source_entity.count() == 1:
            return source_entity[0]
        else:
            new_source_entity = SourceEntity(name=name, reference=source_reference, created_by=author, entity=entity_class)
            new_source_entity.save()
            self.create_entity_relation(new_source_entity)
            return new_source_entity
        
    def create_entity_relation(self, source_entity):
        """ 
        Creates a new entity relation for the given source_entity
        """
        found_entity_relation = EntityRelation.objects.is_active().filter(
            source_entity__name__iexact=source_entity.name).filter(
            data_status_id=5).filter(
            master_entity__reference_id=4).filter(
            relation__name__iexact='Taxon Match')
        if found_entity_relation.count() == 1:
            EntityRelation(master_entity=found_entity_relation[0].master_entity
                            ,source_entity=source_entity
                            ,relation=found_entity_relation[0].relation
                            ,data_status=found_entity_relation[0].data_status
                            ,relation_status=found_entity_relation[0].relation_status
                            ,remarks=found_entity_relation[0].remarks).save()
        else:
            self.create_and_link_entity_relation_from_api(source_entity)
            
    def create_and_link_entity_relation_from_api(self, source_entity):
        """ 
        Creates a new entity relation for the given source_entity from ITIS API
        """
        api_result = self.get_food_item(source_entity.name)["data"][0]
        if api_result:
            canonical_form = api_result["results"][0]["canonical_form"]
            master_entity_result = MasterEntity.objects.filter(name=canonical_form, entity_id=source_entity.entity_id,reference_id=4)
            if master_entity_result:
               return EntityRelation(master_entity=master_entity_result[0],
                                source_entity=source_entity,
                                relation_id=1,
                                data_status_id=5,
                                relation_status_id=1,
                                remarks=master_entity_result[0].reference).save()
        else:
            return None
        
    def get_food_item(self, food): 
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
    
    def get_or_create_source_location(self, location: str, source_reference: SourceReference, author: User):
        """
        Return SourceLocation object for the given location or create a new one
        """
        try:
            source_location = SourceLocation.objects.filter(name__iexact=location, reference=source_reference)
        except Exception as error:
            raise Exception(str(error))
        if source_location.count() == 1:
            return source_location[0]
        else:
            new_source_location = SourceLocation(name=location, reference=source_reference, created_by=author)
            new_source_location.save()
            return new_source_location
        
    def get_or_create_time_period(self, time_period: str, source_reference: SourceReference, author: User):
        """
        Return TimePeriod object for the given time_period or create a new one
        """
        time_period = TimePeriod.objects.filter(name__iexact=time_period, reference=source_reference)
        if time_period.count() == 1:
            return time_period[0]
        else:
            new_time_period = TimePeriod(name=time_period, reference=source_reference, created_by=author)
            new_time_period.save()
            return new_time_period
        
    def get_or_create_source_method(self, method: str, source_reference: SourceReference, author: User):
        """
        Return SourceMethod object for the given method or create a new one
        """
        source_method = SourceMethod.objects.filter(name__iexact=method, reference=source_reference)
        if source_method.count() == 1:
            return source_method[0]
        else:
            new_source_method = SourceMethod(name=method, reference=source_reference, created_by=author)
            new_source_method.save()
            return new_source_method
        
    def get_choicevalue(self, gender: str):
        """
        Return choice value.
        """
        if gender == 'nan':
            return None
        if gender != '22' or gender != '23':
            return None
        choicevalue = ChoiceValue.objects.filter(pk=gender)
        return choicevalue[0]
    
    def possible_nan_to_zero(self, size):
        if size != size or size == 'nan':
            return 0
        return size

    def possible_nan_to_none(self, possible):
        if possible != possible or possible == 'nan':
            return None
        return possible
    

    def create_return_data(self, tsn, scientific_name, status='valid'):
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

    def create_tsn(self, results, tsn):
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
            accepted_results = self.get_accepted_tsn(tsn)
            accepted_taxonomic_unit = self.create_tsn(accepted_results, int(accepted_results['data'][0]['results'][0]['taxon_id']))
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

    def get_accepted_tsn(self, tsn):
        response = itis.GetAcceptedNamesfromTSN(tsn)
        accepted_tsn = response["acceptedNames"][0]["acceptedTsn"]
        scientific_name = response["acceptedNames"][0]["acceptedName"]
        return_data = self.create_return_data(accepted_tsn, scientific_name)
        
        return return_data

    def generate_rank_id(self, food):
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
            results = self.get_fooditem_json(query)
            if len(results['data'][0]) > 0:
                rank = int(itis.getTaxonomicRankNameFromTSN(results['data'][0]['results'][0]['taxon_id'])['rankId'])
                rank_id[rank] = results
                break
            if head >= len(associated_taxa):
                break
        return rank_id

    def trim(self, text:str):
        return " ".join(text.split())

    def trim_df(self, df):
        headers = df.columns
        for i, row in df.iterrows():
            for header in headers:
                df.at[i, header] = self.trim(str(df.at[i, header]))

    def title_matches_citation(self, title, source_citation):
        # https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
        title_without_html = re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', '', title)
        title_without_space = re.sub(r'\s+', '', title_without_html)
        source_citation_without_html = re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', '', source_citation)
        source_citation_without_space = re.sub(r'\s+', '', source_citation_without_html)

        if title_without_space.lower() not in source_citation_without_space.lower():
            return False
        return True


    def convert_empty_values_pa(self, row, headers, pa_item_dict):
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
                value = self.possible_nan_to_none(value)
                pa_item_dict_new[proximate_analysis_item_headers[header]["name"]] = value

        return pa_item_dict_new

    def generate_standard_values_pa(self, items):
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


