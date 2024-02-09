from imports.importers.base_importer import BaseImporter
from ..tools import messages, possible_nan_to_none, possible_nan_to_zero
from mb.models.models import SourceAttribute, SourceReference, SourceEntity, SourceMethod, SourceUnit, ChoiceValue, SourceStatistic, SourceChoiceSetOption, SourceChoiceSetOptionValue, SourceMeasurementValue
from django.db import transaction
from django.contrib.auth.models import User
from mb.models.occurrence_models import Occurrence, Event

class OccurrencesImporter(BaseImporter):

    
    
    @transaction.atomic
    def importRow(self, row, headers, importing_errors):
        
        # Common assignments
        try:
            author = self.get_author(getattr(row, 'author')) # ei oikeasti näin!!!
            reference = self.get_or_create_source_reference(getattr(row, 'references'), author)
            entityclass = self.get_or_create_entity_class(getattr(row, 'taxonRank'), author)
            verbatimScientificname = self.get_or_create_source_entity(getattr(row, 'verbatimScientificName'), reference, entityclass, author)
            #print("common assigments success")
        except Exception as e:
            """
            We don't add anything if we encounter an error.
            """
            importing_errors.append(str(row))
            print("tapahtui virhe: " + str(e))
            return False
        

        


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
            #create source location model
            new_source_location = self.get_or_create_source_location(getattr(row, 'verbatimLocality'), reference, author)
            print("source location created " + str(new_source_location))
            new_event, created = Event.objects.get_or_create(verbatim_event_date=getattr(row, 'verbatimEventDate'))
            print("event created " + str(new_event))

            obj, created = Occurrence.objects.get_or_create(source_reference=reference, event=new_event, source_location=new_source_location, source_entity=verbatimScientificname,
                                                       organism_quantity=getattr(row, 'organismQuantity'), organism_quantity_type=getattr(row, 'organismQuantityType'), gender=self.get_choicevalue(getattr(row, 'sex')), 
                                                       life_stage=self.get_choicevalue(getattr(row, 'lifeStage')),
                                                       occurrence_remarks=getattr(row, 'occurrenceRemarks'), associated_references=getattr(row, 'associatedReferences'))
            if created:
                print("New Occurrence created " + str(obj))
            else:
                print("Existing Occurrence found")
            return True
        except Exception as error:
            print("error in importing: " + str(error))
            return False
     
    


OccurrencesImpoter = OccurrencesImporter()
