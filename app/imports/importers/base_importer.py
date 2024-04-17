import re
from django.db import transaction
from django.contrib.auth.models import User
import pandas as pd
import requests
from mb.models import (
    SourceReference,
    MasterReference,
    EntityClass,
    SourceEntity,
    EntityRelation,
    MasterEntity,
    TimePeriod,
    SourceMethod,
    ChoiceValue,
    SourceLocation,
    FoodItem)
from datetime import timedelta
from config.settings import ITIS_CACHE
import itis.views as itis
import json
import logging
from itis.tools import getFullHierarchyFromTSN, hierarchyToString, GetAcceptedNamesfromTSN, getTaxonomicRankNameFromTSN
from itis.models import TaxonomicUnits, SynonymLinks
from itis.models import TaxonomicUnits, Kingdom, TaxonUnitTypes
from decimal import Decimal
from django.contrib import messages
from requests_cache import CachedSession
import re


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
        
    def search_food_item(self, food):
        queries = self.clean_query(food)
        url = 'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey='
        
        try:
            session = CachedSession(ITIS_CACHE, expire_after=timedelta(days=30), stale_if_error=True)
            for query in queries:
                file = session.get(url+query)
                data = file.text
                if json.loads(data)['itisTerms'][0] != None:
                    break
                  
        except (ConnectionError, UnicodeError):
            return {'data': [{}]}
        
        try:
            taxon_data = json.loads(data)['itisTerms'][0]
        except UnicodeDecodeError:
            taxon_data = json.loads(data.decode('utf-8', 'ignore'))['itisTerms'][0]
        return_data = {}
        if taxon_data and taxon_data['scientificName'].lower():
            tsn = taxon_data['tsn']
            scientific_name = taxon_data['scientificName']
            return_data = self.create_return_data(tsn, scientific_name, status=taxon_data['nameUsage'])
        else:
            return {'data': [{}]}
        return return_data
    
    def clean_query(self, food):
        cleaned_food = re.sub(r'\b(sp|ssp|af|aff|gen)\.?|[\(\)\-]', '', food.lower()).capitalize()
        parts = cleaned_food.split()
        queries = ['%20'.join(parts[:3]).lower(),
                '%20'.join(parts[1:3]).lower(),
                '%20'.join(parts[:1]).lower()]
        return queries

    
    def create_return_data(self, tsn, scientific_name, status='valid'):
        hierarchy = None
        classification_path = ""
        classification_path_ids = ""
        classification_path_ranks = ""
        if status in {'valid', 'accepted'}:
            hierarchy = getFullHierarchyFromTSN(tsn)
            classification_path = hierarchyToString(scientific_name, hierarchy, 'hierarchyList', 'taxonName')
            classification_path_ids = hierarchyToString(tsn, hierarchy, 'hierarchyList', 'tsn', stop_index=classification_path.count("-"))
            classification_path_ranks = hierarchyToString('Species', hierarchy, 'hierarchyList', 'rankName', stop_index=classification_path.count("-"))
        return_data = {
            'taxon_id': tsn,
            'canonical_form': scientific_name,
            'classification_path_ids': classification_path_ids,
            'classification_path': classification_path,
            'classification_path_ranks': classification_path_ranks,
            'taxonomic_status':status
        }
        return {'data': [{'results': [return_data]}]}
    
    def get_accepted_tsn(self, tsn):
        response = GetAcceptedNamesfromTSN(tsn)
        accepted_tsn = response["acceptedNames"][0]["acceptedTsn"]
        scientific_name = response["acceptedNames"][0]["acceptedName"]
        return_data = self.create_return_data(accepted_tsn, scientific_name)
    
        return return_data
    
    def create_tsn(self, results, tsn):
        taxonomic_unit = TaxonomicUnits.objects.filter(tsn=tsn)
        if len(taxonomic_unit)==0:
            completename = results['data'][0]['results'][0]['canonical_form']
            print('completename:', completename)
            hierarchy_string = results['data'][0]['results'][0]['classification_path_ids']
            print('hierarcy_string:', hierarchy_string)
            hierarchy = results['data'][0]['results'][0]['classification_path']
            print('hierarcy:', hierarchy)
            kingdom_id = 0
            rank = 0
    
            if len(hierarchy)>0:
                kingdom = hierarchy.replace('|', '-').split('-')[0]
                print('kingdom:', kingdom)
                kingdom_id = Kingdom.objects.filter(name=kingdom)[0].pk
                print('kingdom_id:', kingdom_id)
                path_rank = results['data'][0]['results'][0]['classification_path_ranks'].replace('|', '-').split('-')[-1]
                print('pathrank:', path_rank)
                rank = TaxonUnitTypes.objects.filter(rank_name=path_rank, kingdom_id=kingdom_id).first().pk
                print('rank:', rank)

    
            taxonomic_unit = TaxonomicUnits(tsn=tsn, kingdom_id=kingdom_id, rank_id=rank, completename=completename, hierarchy_string=hierarchy_string, hierarchy=hierarchy, common_names=None, tsn_update_date=None)
            taxonomic_unit.save()
        else:
            taxonomic_unit = taxonomic_unit.first()
    
        print('täällä 4')
        if results['data'][0]['results'][0]['taxonomic_status'] in ("invalid", "not accepted"):
            accepted_results = self.get_accepted_tsn(tsn)
            accepted_taxonomic_unit = self.create_tsn(accepted_results, int(accepted_results['data'][0]['results'][0]['taxon_id']))
            sl_qs = SynonymLinks.objects.all().filter(tsn = tsn)
            print('täällä 5')
            if len(sl_qs) == 0:
                sl = SynonymLinks(tsn = taxonomic_unit, tsn_accepted = accepted_taxonomic_unit, tsn_accepted_name = accepted_taxonomic_unit.completename)
                sl.save()
            else:
                sl = sl_qs[0]
            taxonomic_unit.hierarchy_string = accepted_taxonomic_unit.hierarchy_string
            taxonomic_unit.hierarchy = accepted_taxonomic_unit.hierarchy
            taxonomic_unit.kingdom_id = accepted_taxonomic_unit.kingdom_id
            taxonomic_unit.rank_id = accepted_taxonomic_unit.rank_id
            taxonomic_unit.save()
        print('täällä 6')
        return taxonomic_unit
    
    def create_fooditem(self, results, food_upper, part):
        print('täällä 3')
        key = next(iter(results))
        print('key:', key)
        tsn = int(results['data'][0]['results'][0]['taxon_id'])
        print('taxon_id:', tsn)
        taxonomic_unit = self.create_tsn(results, tsn)
        print('taxonomicunit:', taxonomic_unit, type(taxonomic_unit))
        print('name:', food_upper, type(food_upper))
        print('part:', part, type(part))
        print('täällä 7')
        food_item_exists = FoodItem.objects.filter(name__iexact=food_upper)
        print('täällä 8')
        if len(food_item_exists) > 0:
            return food_item_exists[0]
        else:
            print('täällä 9')
            food_item = FoodItem(name=food_upper, is_cultivar=False, pa_tsn=taxonomic_unit, part=part, tsn=taxonomic_unit)
            print(food_item)
            print(type(food_item))
            print('täällä 10')
            food_item.save()
        print('täällä 11')
        return food_item
    
    def generate_rank_id(self, food):
        rank_id = {}
        results = self.search_food_item(food)
        print(results)
        if len(results['data'][0]) > 0:
            rank = int(getTaxonomicRankNameFromTSN(results['data'][0]['results'][0]['taxon_id'])['rankId'])
            rank_id[rank] = results
        print('täällä 1')
        print('rankid:', rank_id)
        return rank_id
    

    def get_fooditem(self, food, part):
        food_upper = food.upper()
        print('foodupper:', food_upper)
        food_item = FoodItem.objects.filter(name__iexact=food_upper)
        print('fooditem:', food_item)
        print('täällä 0')
        if len(food_item) > 0:
            print('pitäisi olla täällä')
            print('fooditemfirst:', food_item.first())
            return food_item.first()

        rank_id = self.generate_rank_id(food)
        print('täällä 2')
        if len(rank_id) == 0:
            food_item = FoodItem(name=food_upper, part=part, tsn=None, pa_tsn=None, is_cultivar=0)
            food_item.save()
            return food_item
        return self.create_fooditem(rank_id[max(rank_id)], food_upper, part)
    
    
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
        time_period1 = TimePeriod.objects.filter(name__iexact=time_period, reference=source_reference)
        if time_period1.exists():
            return time_period1[0]  # Return the first matching object
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
        else:
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

    


