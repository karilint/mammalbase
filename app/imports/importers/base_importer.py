import re
from django.db import transaction
import pandas as pd
import requests
from mb.models.models import SourceReference, MasterReference, EntityClass, SourceEntity, EntityRelation, MasterEntity, TimePeriod, SourceMethod, ChoiceValue
from mb.models.location_models import SourceLocation
from mb.models.habitat_models import SourceHabitat
from ..tools import make_harvard_citation_journalarticle
from datetime import timedelta
from config.settings import ITIS_CACHE
from requests_cache import CachedSession
import itis.views as itis
import json
from django.contrib.auth.models import User
class BaseImporter:
    """
    Base class for all importers
    """

    @transaction.atomic
    def importRow(self, row : pd.Series):
        pass
    
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
            volume = item.get('volume', '')
            issue = item.get('issue', '')
            page = item.get('page', '')
            ref_type = item.get('type', '')

            # Create citation based on type
            if ref_type == 'journal-article':
                citation = make_harvard_citation_journalarticle(title, doi, authors, year, container_title, volume, issue, page)
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
    
    # TÄMÄ ON VIRHEELLINEN! MasterReferencellä ei ole kenttää source_reference
    #def get_or_create_master_reference(self, source_reference: SourceReference, author: User):
        """
        Return MasterReference object for the given source_reference
        """
        
        """
        master_reference = MasterReference.objects.filter(source_reference=source_reference)
        if master_reference.count() == 1:
            return master_reference[0]
        else:
            new_master_reference = self.get_master_reference_from_cross_ref(source_reference.citation, author)
            if new_master_reference:                                                                                                                          
                return new_master_reference
            else:
                return None
        """
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
        # here add a real validation for citation and author
        if (citation.lower() == "nan" or citation == None) or (str(author).lower() == "nan" or author == None):
            raise Exception("SourceReference is not valid!")

        source_reference = SourceReference.objects.filter(citation__iexact=citation)
        
        if source_reference.count() == 1:
            return source_reference[0]
        
        
        new_reference = SourceReference(citation=citation,status=1, created_by=author)
        master_reference = self.get_or_create_master_reference(citation, author)
        new_reference.master_reference = master_reference
        new_reference.save()
        print("uusi master reference luotu " + str(new_reference))

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
                                source_entity=source_entity.id,
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
            print("virhe" + str(error))
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
        if gender == 'nan':
            return None
        if gender != '22' or gender != '23':
            return None
        choicevalue = ChoiceValue.objects.filter(pk=gender)
        return choicevalue[0]
    
    def get_or_create_source_habitat(self, habitat_type: str, habitat_percentage: str, author: User):
        """
        Return SourceHabitat object for the given habitat_type or create a new one
        """
        source_habitat = SourceHabitat.objects.filter(habitat_type__iexact=habitat_type)
        if source_habitat.count() == 1:
            return source_habitat[0]
        else:
            new_source_habitat = SourceHabitat(habitat_type=habitat_type, habitat_percentage=habitat_percentage, created_by=author)
            new_source_habitat.save()
            return new_source_habitat
            
        
        
        

    