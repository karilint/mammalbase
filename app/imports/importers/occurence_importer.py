from imports.importers.base_importer import BaseImporter
from django.db import transaction
from mb.models import DietSet, DietSetItem
from ..tools import possible_nan_to_none, possible_nan_to_zero, get_choicevalue

class DietImporter(BaseImporter):
    
    @transaction.atomic
    def importRow(self, row):
        headers = list(row.columns.values)
        
        # Common assignments
        author = self.get_author(getattr(row, 'author'))
        reference = self.get_or_create_source_reference(getattr(row, 'references'), author)
        entityclass = self.get_or_create_entity_class(getattr(row, 'taxonRank'), author)
        taxon = self.get_or_create_source_entity(getattr(row, 'verbatimScientificName'), reference, entityclass, author)
        
        column_functions = {
            'sex': get_choicevalue,
            'individualCount': possible_nan_to_zero,
            'associatedReferences': possible_nan_to_none,
            'samplingEffort': lambda val: self.get_or_create_time_period(val, reference, author),
            'measurementMethod': lambda val: self.get_or_create_source_method(val, reference, author),
            'verbatimEventDate': possible_nan_to_none,
            'verbatimLocality': lambda val: self.get_or_create_source_location(val, reference, author),
        }
        
        # Dictionary comprehension for conditional assignments
        row_data = {key: func(getattr(row, key)) for key, func in column_functions.items() if key in headers}

        # Ensure default values for keys not in headers
        default_values = {'location': None, 'gender': None, 'sample_size': 0, 'cited_reference': None, 'time_period': None, 'method': None, 'study_time': None}
        row_data = {**default_values, **row_data}


        # Creating or retrieving DietSet object
        ds_kwargs = {'reference': reference, 'taxon': taxon, 'created_by': author, **row_data}
        
        # Rename keys to match model attributes
        model_attribute_mapping = {
            'sex': 'gender',
            'individualCount': 'sample_size',
            'associatedReferences': 'cited_reference',
            'samplingEffort': 'time_period',
            'measurementMethod': 'method',
            'verbatimEventDate': 'study_time',
            'verbatimLocality': 'location',
        }
        for key, value in model_attribute_mapping.items():
            if key in ds_kwargs:
                ds_kwargs[value] = ds_kwargs.pop(key)
        
        ds, created = DietSet.objects.get_or_create(**ds_kwargs)
        if created:
            print("New DietSet created:", ds)
        else:
            print("Existing DietSet found:", ds)

        # Create DietSet item
        self.create_diet_set_item(row, ds)
        
        
    def create_diet_set_item(self, row, diet_set: DietSet):
        """
        Creates a DietSetItem object from a row of data and a DietSet object.
        """
        headers = list(row.columns.values)
        if 'PartOfOrganism' in headers:
            food_item = self.get_food_item(getattr(row, 'verbatimAssociatedTaxa'), possible_nan_to_none(getattr(row, 'PartOfOrganism')))
        else:
            food_item = self.get_food_item(getattr(row, 'verbatimAssociatedTaxa'), None)
        list_order = getattr(row, 'sequence')
        if 'measurementValue' in headers:
            percentage = round(possible_nan_to_zero(getattr(row, 'measurementValue')), 3)
        else:
            percentage = 0
        old_ds = DietSetItem.objects.filter(diet_set=diet_set, food_item=food_item, list_order=list_order)

        if len(old_ds) == 0:
            dietsetitem = DietSetItem(diet_set=diet_set, food_item=food_item, list_order=list_order, percentage=percentage) 
            dietsetitem.save()

DietImpoter = DietImporter()
