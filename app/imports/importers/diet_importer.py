"""Imports diet data
"""
import json
import re
from datetime import timedelta
from django.db import transaction
from mb.models import DietSet, DietSetItem
from mb.models import ChoiceValue, FoodItem
from itis.tools import getFullHierarchyFromTSN, hierarchyToString, GetAcceptedNamesfromTSN, getTaxonomicRankNameFromTSN
from itis.models import TaxonomicUnits, Kingdom, TaxonUnitTypes, SynonymLinks
from requests_cache import CachedSession
from config.settings import ITIS_CACHE
from .base_importer import BaseImporter


class DietImporter(BaseImporter):
    """Class for diet importer
    """
    @transaction.atomic
    def importRow(self, row):

        # Common assignments for diet set
        author = self.get_author(getattr(row, 'author'))
        reference = self.get_or_create_source_reference(
            getattr(row, 'references'), author)
        entityclass = self.get_or_create_entity_class(
            getattr(row, 'taxonRank'), author)
        taxon = self.get_or_create_source_entity(
            getattr(
                row,
                'verbatimScientificName'),
            reference,
            entityclass,
            author)
        method = self.get_or_create_source_method(
            getattr(row, 'measurementMethod'), reference, author)
        time_period = self.get_or_create_time_period(
            (getattr(row, 'samplingEffort')), reference, author)
        cited_reference=self.possible_nan_to_none(getattr(
                row,
                'associatedReferences'))
        sample_size=self.possible_nan_to_zero(
                getattr(
                    row,
                    'individualCount'))
        study_time=self.possible_nan_to_none(getattr(
                row,
                'verbatimEventDate'))

        # Create source location
        new_source_location = self.get_or_create_source_location(
            getattr(row, 'verbatimLocality'), reference, author)

        # Check choice values
        gender = str(getattr(row, 'sex'))

        part_of_organism = str(getattr(row, 'PartOfOrganism'))

        if gender == "nan" or gender == "":
            gender = None
        else:
            gender = ChoiceValue.objects.filter(
                choice_set="Gender", caption__iexact=gender).first()
            if not gender:
                gender = None

        if part_of_organism == "nan" or part_of_organism == "":
            part_of_organism = None
        else:
            part_of_organism = ChoiceValue.objects.filter(
                choice_set="FoodItemPart", caption__iexact=part_of_organism).first()
            if not part_of_organism:
                part_of_organism = None

        # Create diet set
        obj = DietSet.objects.filter(
            reference=reference,
            cited_reference=cited_reference,
            taxon=taxon,
            gender=gender,
            location=new_source_location,
            sample_size=sample_size,
            time_period=time_period,
            method=method,
            study_time=study_time).first()
        if not obj:
            obj = DietSet.objects.create(
                reference=reference,
                cited_reference=cited_reference,
                taxon=taxon,
                gender=gender,
                location=new_source_location,
                sample_size=sample_size,
                time_period=time_period,
                method=method,
                study_time=study_time,
                created_by=author)
            print("Diet set created")

        # Common assignments for diet set item
        verbatim_associated_taxa = str(getattr(row, 'verbatimAssociatedTaxa'))
        if verbatim_associated_taxa == "nan" or verbatim_associated_taxa == "":
            food_item = None
        else:
            food_item = self.get_or_create_fooditem(
                getattr(row, 'verbatimAssociatedTaxa'), part_of_organism)
        list_order = getattr(row, 'sequence')
        percentage = self.possible_nan_to_zero(
            getattr(row, 'measurementValue'))

        # Create diet set item
        diet_set_item = DietSetItem.objects.filter(
            diet_set=obj, food_item=food_item, percentage=percentage)

        if diet_set_item.exists():
            print("Diet set item link exists")
            return False
        DietSetItem.objects.create(
            diet_set=obj,
            food_item=food_item,
            list_order=list_order,
            percentage=percentage)
        print("Diet set item link created")
        return True

    def search_food_item(self, query):
        url = 'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey='

        try:
            session = CachedSession(
                ITIS_CACHE, expire_after=timedelta(
                    days=30), stale_if_error=True)
            file = session.get(url + query.lower().capitalize())
            data = file.text
        except (ConnectionError, UnicodeError):
            return {'data': [{}]}

        try:
            taxon_data = json.loads(data)['itisTerms'][0]
        except UnicodeDecodeError:
            taxon_data = json.loads(data.decode(
                'utf-8', 'ignore'))['itisTerms'][0]
        except json.JSONDecodeError:
            return {'data': [{}]}
        return_data = {}
        if taxon_data and taxon_data['scientificName'].lower(
        ) == query.lower():
            tsn = taxon_data['tsn']
            scientific_name = taxon_data['scientificName']
            return_data = self.create_return_data(
                tsn, scientific_name, status=taxon_data['nameUsage'])
        else:
            return {'data': [{}]}
        return return_data

    def create_return_data(self, tsn, scientific_name, status='valid'):
        hierarchy = None
        classification_path = ""
        classification_path_ids = ""
        classification_path_ranks = ""
        if status in {'valid', 'accepted'}:
            hierarchy = getFullHierarchyFromTSN(tsn)
            classification_path = hierarchyToString(
                scientific_name, hierarchy, 'hierarchyList', 'taxonName')
            classification_path_ids = hierarchyToString(
                tsn,
                hierarchy,
                'hierarchyList',
                'tsn',
                stop_index=classification_path.count("-"))
            classification_path_ranks = hierarchyToString(
                'Species',
                hierarchy,
                'hierarchyList',
                'rankName',
                stop_index=classification_path.count("-"))
        return_data = {
            'taxon_id': tsn,
            'canonical_form': scientific_name,
            'classification_path_ids': classification_path_ids,
            'classification_path': classification_path,
            'classification_path_ranks': classification_path_ranks,
            'taxonomic_status': status
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
        if len(taxonomic_unit) == 0:
            completename = results['data'][0]['results'][0]['canonical_form']
            hierarchy_string = results['data'][0]['results'][0]['classification_path_ids']
            hierarchy = results['data'][0]['results'][0]['classification_path']
            kingdom_id = 0
            rank = 0

            if len(hierarchy) > 0:
                kingdom = hierarchy.replace('|', '-').split('-')[0]
                kingdom_id = Kingdom.objects.filter(name=kingdom)[0].pk
                path_rank = results['data'][0]['results'][0]['classification_path_ranks'].replace(
                    '|', '-').split('-')[-1]
                rank = TaxonUnitTypes.objects.filter(
                    rank_name=path_rank, kingdom_id=kingdom_id).first().pk

            taxonomic_unit = TaxonomicUnits(
                tsn=tsn,
                kingdom_id=kingdom_id,
                rank_id=rank,
                completename=completename,
                hierarchy_string=hierarchy_string,
                hierarchy=hierarchy,
                common_names=None,
                tsn_update_date=None)
            taxonomic_unit.save()
        else:
            taxonomic_unit = taxonomic_unit.first()

        if results['data'][0]['results'][0]['taxonomic_status'] in (
                "invalid", "not accepted"):
            accepted_results = self.get_accepted_tsn(tsn)
            accepted_taxonomic_unit = self.create_tsn(accepted_results, int(
                accepted_results['data'][0]['results'][0]['taxon_id']))
            sl_qs = SynonymLinks.objects.all().filter(tsn=tsn)
            if len(sl_qs) == 0:
                sl = SynonymLinks(
                    tsn=taxonomic_unit,
                    tsn_accepted=accepted_taxonomic_unit,
                    tsn_accepted_name=accepted_taxonomic_unit.completename)
                sl.save()
            else:
                sl = sl_qs[0]
            taxonomic_unit.hierarchy_string = accepted_taxonomic_unit.hierarchy_string
            taxonomic_unit.hierarchy = accepted_taxonomic_unit.hierarchy
            taxonomic_unit.kingdom_id = accepted_taxonomic_unit.kingdom_id
            taxonomic_unit.rank_id = accepted_taxonomic_unit.rank_id
            taxonomic_unit.save()
        return taxonomic_unit

    def create_fooditem(self, results, food_upper, part):
        tsn = int(results['data'][0]['results'][0]['taxon_id'])
        taxonomic_unit = self.create_tsn(results, tsn)
        food_item_exists = FoodItem.objects.filter(name__iexact=food_upper)
        if len(food_item_exists) > 0:
            return food_item_exists[0]
        food_item = FoodItem(
            name=food_upper,
            is_cultivar=False,
            pa_tsn=taxonomic_unit,
            part=part,
            tsn=taxonomic_unit)
        food_item.save()
        return food_item

    def generate_rank_id(self, food):
        associated_taxa = re.sub(
            r'\b(?:aff|gen|bot|zoo|ssp|subf|exx|indet|subsp|subvar|var|nothovar|group|forma)\.?|\b\w{1,2}\b|\s*\W',
            ' ',
            food).strip().split()
        head = 0
        tail = 0
        rank_id = {}
        if associated_taxa:
            while True:
                if head == tail:
                    query = associated_taxa[tail]
                    head += 1
                else:
                    query = associated_taxa[tail] + " " + associated_taxa[head]
                    tail += 1
                results = self.search_food_item(query)
                if len(results['data'][0]) > 0:
                    rank = int(
                        getTaxonomicRankNameFromTSN(
                            results['data'][0]['results'][0]['taxon_id'])['rankId'])
                    rank_id[rank] = results
                    break
                if head >= len(associated_taxa):
                    print(f"Food item '{food}' not found in api")
                    break
        return rank_id

    def get_or_create_fooditem(self, food, part):
        food_upper = food.upper()
        food_item = FoodItem.objects.filter(name__iexact=food_upper)
        if len(food_item) > 0:
            return food_item.first()

        rank_id = self.generate_rank_id(food)
        if not rank_id:
            food_item = FoodItem(name=food_upper, part=part,
                                 tsn=None, pa_tsn=None, is_cultivar=0)
            food_item.save()
            return food_item
        return self.create_fooditem(rank_id[max(rank_id)], food_upper, part)
