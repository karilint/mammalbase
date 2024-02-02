from imports.importers.base_importer import BaseImporter
from ..tools import possible_nan_to_none, possible_nan_to_zero
from mb.models.models import SourceAttribute, SourceReference, SourceEntity, SourceMethod, SourceUnit, ChoiceValue, SourceStatistic, SourceChoiceSetOption, SourceChoiceSetOptionValue, SourceMeasurementValue
from django.db import transaction
from django.contrib.auth.models import User
from mb.models.occurrence_models import Occurrence

class OccurrencesImporter(BaseImporter):
    
    @transaction.atomic
    def importRow(self, row, headers):
        
        # Common assignments
        #author = self.get_author(getattr(row, 'author')) # toimii jos tyyliin 
        author = "admin" 
        reference = self.get_or_create_source_reference(getattr(row, 'references'), author)
        entityclass = self.get_or_create_entity_class(getattr(row, 'taxonRank'), author)
        verbatimScientificname = self.get_or_create_source_entity(getattr(row, 'verbatimScientificName'), reference, entityclass, author)


        # Maybe neccessary later?
        column_functions = {
            "source_reference" : reference,
            "event" : None,
            "source_locality" : None,
            "source_entity" : None,
            "organism_quantity" : getattr(row, 'organismQuantity'),
            "organism_quantity_type" : getattr(row, 'organismQuantityType'),
            "verbatim_scientific_name" : verbatimScientificname,  # NOT IN USE!        
            "gender" : self.get_choicevalue(getattr(row, 'sex')),
            "life_stage" : self.get_choicevalue(getattr(row, 'lifeStage')),
            "occurrence_remarks" : getattr(row, 'occurrenceRemarks'),
            "associated_references" : getattr(row, 'associatedReferences'),
        }
        
        created = None
        try:
            created = Occurrence.objects.get_or_create(source_reference=reference, event=None, source_locality=None, source_entity=None,
                                                       organism_quantity=getattr(row, 'organismQuantity'), organism_quantity_type=getattr(row, 'organismQuantityType'), gender=self.get_choicevalue(getattr(row, 'sex')), 
                                                       life_stage=self.get_choicevalue(getattr(row, 'lifeStage')),
                                                       occurrence_remarks=getattr(row, 'occurrenceRemarks'), associated_references=getattr(row, 'associatedReferences'))
            if created:
                print("New Occurrence created " + str(created))
            else:
                print("Existing Occurrence found")
            return True
        except Exception as error:
            print("error in importing: " + str(error))
            return False
     
    


OccurrencesImpoter = OccurrencesImporter()
