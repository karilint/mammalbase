from django.db import transaction
from mb.models import DietSet, DietSetItem, Event, SourceHabitat
from .base_importer import BaseImporter

class DietImporter(BaseImporter):
    
    @transaction.atomic
    def importRow(self, row):

        
        ## Common assignments
        author = self.get_author(getattr(row, 'author'))
        reference = self.get_or_create_source_reference(getattr(row, 'references'), author)
        entityclass = self.get_or_create_entity_class(getattr(row, 'taxonRank'), author)
        verbatimScientificname = self.get_or_create_source_entity(getattr(row, 'verbatimScientificName'), reference, entityclass, author)
        taxon = self.get_or_create_source_entity(getattr(row, 'verbatimScientificName'), reference, entityclass, author)
        habitat, created = SourceHabitat.objects.get_or_create(habitat_type=getattr(row, 'habitatType'), habitat_percentage=getattr(row, 'habitatPercentage'), source_reference=reference, created_by=author)

        created = None
        
        # Create source location model
        new_source_location = self.get_or_create_source_location(getattr(row, 'verbatimLocality'), reference, author)
        new_event, created = Event.objects.get_or_create(verbatim_event_date=getattr(row, 'verbatimEventDate'), source_habitat=habitat)

                
        
        
        obj, created = DietSet.objects.get_or_create(source_reference=reference, event=new_event, source_location=new_source_location, source_entity=verbatimScientificname,
                                                    organism_quantity=getattr(row, 'organismQuantity'), organism_quantity_type=getattr(row, 'organismQuantityType'), taxon=taxon, 
                                                    occurrence_remarks=getattr(row, 'occurrenceRemarks'), associated_references=getattr(row, 'associatedReferences'))
        if created:
            return True
        else:
            return False