import re
from datetime import timedelta
import json
from django.db import transaction
from django.contrib.auth.models import User
import pandas as pd
import requests
from requests_cache import CachedSession
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
    SourceLocation)
import re
from requests_cache import CachedSession
from datetime import timedelta
from config.settings import ITIS_CACHE


class BaseImporter:
    """
    Base class for all importers
    """

    @transaction.atomic
    def importRow(self, row: pd.Series):
        pass

    def make_harvard_citation_journalarticle(
            self, title, doi, authors, year, container_title, volume, issue, page):
        citation = ""
        for author in authors:
            if authors.index(author) == len(authors) - 1:
                citation += str(author)
            else:
                citation += str(author) + ", "

        citation += " " + str(year) + ". " + str(title) + ". " + str(container_title) + ". " + str(
            volume) + "(" + str(issue) + "), pp." + str(page) + ". Available at: " + str(doi) + "."
        return citation

    def get_author(self, social_id: str):
        """
        Return User object for the given social_id
        """
        author = User.objects.filter(socialaccount__uid=social_id)
        if author.count() == 1:
            return author[0]
        raise Exception("Author not found")

    def get_master_reference_from_cross_ref(self, citation: str, user_author: User):
        """
        Gets the master reference from crossref API
        https://api.crossref.org/swagger-ui/index.htm
        """
        formatted_citation = citation.replace(" ", "%20")
        url = (f'https://api.crossref.org/works?query.bibliographic='
               f'"{formatted_citation}"&mailto=kari.lintulaakso@helsinki.fi&rows=2')
        try:
            response = requests.get(url, timeout=300).json()
            items = response.get('message', {}).get('items', [])
            if not items:
                return False

            # Process the first item
            item = items[0]
            title = re.sub(
                '<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', '', item.get('title', [''])[0])
            authors = [
                f"{a['family']}, {a['given'][0]}." for a in item.get('author', [])]
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
                citation = self.make_harvard_citation_journalarticle(
                    title, doi, authors, year, container_title, volume, issue, page)
            else:
                authors_str = ", ".join(authors)
                citation = f"{authors_str} {year}. {title}. Available at: {doi}."

            # Create and save MasterReference
            master_ref = MasterReference(
                type=ref_type, doi=doi, uri=uri, first_author=first_author, year=year,
                title=title, container_title=container_title, volume=volume, issue=issue,
                page=page, citation=citation, created_by=user_author
            )
            master_ref.save()
            print(f"MasterReference created: {master_ref}")
            return master_ref

        except Exception as exc:
            print(f"Error: {exc}")
            return None

    def get_or_create_master_reference(self, citation: str, author: User):
        """
        Return MasterReference object for the given source_reference
        """
        master_reference = MasterReference.objects.filter(citation=citation)
        if master_reference.count() == 1:
            return master_reference[0]
        new_master_reference = self.get_master_reference_from_cross_ref(
            citation, author)
        if new_master_reference:
            return new_master_reference
        return None

    def get_or_create_source_reference(self, citation: str, author: User):
        """
        Return new or exists source reference.
        """
        if ((citation.lower() == "nan" or citation is None) or
                (str(author).lower() == "nan" or author is None)):

            raise Exception("SourceReference is not valid!")

        source_reference = SourceReference.objects.filter(
            citation__iexact=citation)

        if source_reference.count() == 1:
            return source_reference[0]

        new_reference = SourceReference(
            citation=citation, status=1, created_by=author)
        master_reference = self.get_or_create_master_reference(
            citation, author)
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
        new_entity_class = EntityClass(name=taxon_rank, created_by=author)
        new_entity_class.save()
        return new_entity_class

    def get_or_create_source_entity(self, name: str, source_reference: SourceReference,
                                    entity_class: EntityClass, author: User):
        """
        Return SourceEntity object for the given name or create a new one
        """
        source_entity = SourceEntity.objects.filter(
            name__iexact=name, reference=source_reference)
        if source_entity.count() == 1:
            return source_entity[0]
        new_source_entity = SourceEntity(
            name=name, reference=source_reference, created_by=author, entity=entity_class)
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
            EntityRelation(master_entity=found_entity_relation[0].master_entity,
                           source_entity=source_entity, relation=found_entity_relation[0].relation,
                           data_status=found_entity_relation[0].data_status,
                           relation_status=found_entity_relation[0].relation_status,
                           remarks=found_entity_relation[0].remarks).save()
        else:
            self.create_and_link_entity_relation_from_api(source_entity)

    def create_and_link_entity_relation_from_api(self, source_entity):
        """
        Creates a new entity relation for the given source_entity from ITIS API
        """
        name = self.search_scientificName(source_entity.name)
        if name:
            master_entity_result = MasterEntity.objects.filter(name=name, entity_id=source_entity.entity_id,reference_id=4)
            if master_entity_result:
               return EntityRelation(master_entity=master_entity_result[0],
                                source_entity=source_entity,
                                relation_id=1,
                                data_status_id=5,
                                relation_status_id=1,
                                remarks=master_entity_result[0].reference).save()
        else:
            return None    
    
    def get_or_create_source_location(self, location: str, source_reference: SourceReference, author: User):
        """
        Return SourceLocation object for the given location or create a new one
        """
        try:
            source_location = SourceLocation.objects.filter(
                name__iexact=location, reference=source_reference)
        except Exception as error:
            raise Exception(str(error)) from error
        if source_location.count() == 1:
            return source_location[0]
        new_source_location = SourceLocation(
            name=location, reference=source_reference, created_by=author)
        new_source_location.save()
        return new_source_location

    def get_or_create_time_period(self, time_period: str, source_reference: SourceReference,
                                  author: User):
        """
        Return TimePeriod object for the given time_period or create a new one
        """
        time_period = TimePeriod.objects.filter(
            name__iexact=time_period, reference=source_reference)
        if time_period.count() == 1:
            return time_period[0]

        new_time_period = TimePeriod(
            name=time_period, reference=source_reference, created_by=author)
        new_time_period.save()
        return new_time_period

    def get_or_create_source_method(self, method: str, source_reference: SourceReference,
                                    author: User):
        """
        Return SourceMethod object for the given method or create a new one
        """
        source_method = SourceMethod.objects.filter(
            name__iexact=method, reference=source_reference)
        if source_method.count() == 1:
            return source_method[0]

        new_source_method = SourceMethod(
            name=method, reference=source_reference, created_by=author)
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
        if size != size or size == 'nan' or size == "":
            return 0
        return size

    def possible_nan_to_none(self, possible):
        if possible != possible or possible == 'nan':
            return None
        return possible

    def search_scientificName(self, entity_name):
            queries = self.clean_query(entity_name)
            url = 'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey='
            
            try:
                session = CachedSession(ITIS_CACHE, expire_after=timedelta(days=30), stale_if_error=True)
                for query in queries:
                    file = session.get(url+query)
                    data = file.json()
                    if data['itisTerms'][0] != None:
                        break
                    
            except (ConnectionError, UnicodeError):
                return None
            
            taxon_data = data['itisTerms'][0]
            if taxon_data and taxon_data['scientificName'].lower():
                return taxon_data['scientificName']
            else:
                return None

    def clean_query(self, food):
        cleaned_food = re.sub(r'\s*\b(sp|ssp|af|aff|gen)\.?|\s*[\(\)\-]', '', food.lower()).capitalize().strip()
        parts = cleaned_food.split()
        return parts

