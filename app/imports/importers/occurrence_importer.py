from imports.importers.base_importer import BaseImporter
from django.db import transaction
from django.contrib.auth.models import User

from mb.models import (
    SourceAttribute,
    SourceReference,
    SourceEntity,
    SourceMethod,
    SourceUnit,
    ChoiceValue,
    SourceStatistic,
    SourceChoiceSetOption,
    SourceChoiceSetOptionValue,
    SourceMeasurementValue,
    Occurrence,
    Event,
    SourceHabitat)
from .base_importer import BaseImporter

class OccurrencesImporter(BaseImporter):
    
    @transaction.atomic
    def importRow(self, row):
        """Put data of row to database.

        Args:
            row (Pandas): row of tsv
            importing_errors (list): list to possible errors

        Returns:
            bool: True if import is successded, otherwise False.
        """
        # Common assignments
        author = self.get_author(getattr(row, 'author'))
        reference = self.get_or_create_source_reference(getattr(row, 'references'), author)
        entityclass = self.get_or_create_entity_class(getattr(row, 'taxonRank'), author)
        verbatimScientificname = self.get_or_create_source_entity(getattr(row, 'verbatimScientificName'), reference, entityclass, author)
        habitat, created = SourceHabitat.objects.get_or_create(habitat_type=getattr(row, 'habitatType'), habitat_percentage=getattr(row, 'habitatPercentage'), source_reference=reference, created_by=author)

        created = None
        
        # Create source location model
        new_source_location = self.get_or_create_source_location(getattr(row, 'verbatimLocality'), reference, author)
        new_event, created = Event.objects.get_or_create(verbatim_event_date=getattr(row, 'verbatimEventDate'), source_habitat=habitat)

        gender = str(getattr(row, 'sex'))

        life_stage = str(getattr(row, 'lifeStage'))

        if gender == "nan" or gender == "":
            gender = None
        else:

            gender, created = ChoiceValue.objects.get_or_create(choice_set="Gender", caption=gender.capitalize())

        if life_stage == "nan" or life_stage == "":
            life_stage = None
        else:
            life_stage, created = ChoiceValue.objects.get_or_create(choice_set="Lifestage", caption=life_stage.capitalize())
        
        obj, created = Occurrence.objects.get_or_create(source_reference=reference, event=new_event, source_location=new_source_location, source_entity=verbatimScientificname,
                                                    organism_quantity=getattr(row, 'organismQuantity'), organism_quantity_type=getattr(row, 'organismQuantityType'), gender=gender, 
                                                    life_stage=life_stage,
                                                    occurrence_remarks=getattr(row, 'occurrenceRemarks'), associated_references=getattr(row, 'associatedReferences'))
        if created:
            return True
        else:
            return False

