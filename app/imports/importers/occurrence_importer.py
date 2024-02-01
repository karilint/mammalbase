from imports.importers.base_importer import BaseImporter
from django.db import transaction
from mb.models.models import ChoiceValue
from mb.models.occurrence_models import Occurrence

class OccurrencesImporter(BaseImporter):
    
    @transaction.atomic
    def importRow(self, row):
        #headers = list(row.columns.values)
        
        # Common assignments
        author = self.get_author(getattr(row, 'author')) # toimii jos tyyliin author = "kissa"
        reference = self.get_or_create_source_reference(getattr(row, 'references'), author)
        entityclass = self.get_or_create_entity_class(getattr(row, 'taxonRank'), author)
        taxon = self.get_or_create_source_entity(getattr(row, 'verbatimScientificName'), reference, entityclass, author)
        verbatimScientificname = taxon
        
        column_functions = {
            "source_reference" : getattr(row, 'references', author),
            "event" : None,
            "source_locality" : None,
            "source_entity" : None,
            "organism_quantity" : getattr(row, 'organismQuantity'),
            "organism_quantity_type" : getattr(row, 'organismQuantityType'),
            "verbatim_scientific_name" : verbatimScientificname,          
            "gender" : ChoiceValue(getattr(row, 'sex')),
            "life_stage" : ChoiceValue(getattr(row, 'lifeStage')),
            "occurrence_remarks" : getattr(row, 'occurrenceRemarks'),
            "associated_references" : getattr(row, 'associatedReferences'),
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
            print("New  created:", ds)
        else:
            print("Existing DietSet found:", ds)
        
        new_occurrence = Occurrence(**column_functions)
        new_occurrence.save()
    


OccurrencesImpoter = OccurrencesImporter()
