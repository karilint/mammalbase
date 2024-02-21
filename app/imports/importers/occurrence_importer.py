from imports.importers.base_importer import BaseImporter
from ..tools import messages, possible_nan_to_none, possible_nan_to_zero
from mb.models.models import SourceAttribute, SourceReference, SourceEntity, SourceMethod, SourceUnit, ChoiceValue, SourceStatistic, SourceChoiceSetOption, SourceChoiceSetOptionValue, SourceMeasurementValue
from django.db import transaction
from django.contrib.auth.models import User
from mb.models.occurrence_models import Occurrence, Event

class OccurrencesImporter(BaseImporter):

    
    
    @transaction.atomic
    def importRow(self, row, importing_errors):
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
        
        
        created = None
        
        # Create source location model
        new_source_location = self.get_or_create_source_location(getattr(row, 'verbatimLocality'), reference, author)
        new_event, created = Event.objects.get_or_create(verbatim_event_date=getattr(row, 'verbatimEventDate'))
        
        gender = str(getattr(row, 'sex'))
        life_stage = str(getattr(row, 'lifeStage'))

        if gender == "nan":
            gender = None
        else:
            gender, created = ChoiceValue.objects.get_or_create(choice_set="Gender", caption=gender.capitalize())

        if life_stage == "nan":
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
     
    


OccurrencesImpoter = OccurrencesImporter()
