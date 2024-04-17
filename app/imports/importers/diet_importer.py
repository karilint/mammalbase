from django.db import transaction
from mb.models import DietSet, DietSetItem, Event, SourceHabitat
from .base_importer import BaseImporter
from mb.models import ChoiceValue

base_importer = BaseImporter()

class DietImporter(BaseImporter):
    
    @transaction.atomic
    def importRow(self, row):

        
        ## Common assignments
        author = self.get_author(getattr(row, 'author'))
        reference = self.get_or_create_source_reference(getattr(row, 'references'), author)
        entityclass = self.get_or_create_entity_class(getattr(row, 'taxonRank'), author)
        taxon = self.get_or_create_source_entity(getattr(row, 'verbatimScientificName'), reference, entityclass, author)
        habitat, created = SourceHabitat.objects.get_or_create(habitat_type=getattr(row, 'habitat'), source_reference=reference, created_by=author)
        method= self.get_or_create_source_method(getattr(row, 'measurementMethod'), reference, author)
        time_period=self.get_or_create_time_period(getattr(row, 'samplingEffort'), reference, author)
        created = None


        # Create source location model
        new_source_location = self.get_or_create_source_location(getattr(row, 'verbatimLocality'), reference, author)

        gender = str(getattr(row, 'sex'))

        part_of_organism = str(getattr(row, 'PartOfOrganism'))

        if gender == "nan" or gender == "":
            gender = None
        else:
            gender, created = ChoiceValue.objects.get_or_create(choice_set="Gender", caption=gender.capitalize())

        if part_of_organism == "nan" or part_of_organism == "":
            part_of_organism = None
        else:
            part_of_organism = ChoiceValue.objects.filter(choice_set="FoodItemPart", caption=part_of_organism).first()
            if part_of_organism:
                part_of_organism = part_of_organism
            else:
                part_of_organism = None
            
            
                

        obj, created = DietSet.objects.get_or_create(reference=reference, cited_reference=getattr(row, 'associatedReferences'), taxon=taxon, location=new_source_location, sample_size=base_importer.possible_nan_to_zero(getattr(row, 'individualCount')),
                                                     time_period=time_period, method=method, study_time=getattr(row, 'verbatimEventDate'), created_by=author)
        if not created:
            return False
        
        print('partoforganism:', part_of_organism)
        food_item = self.get_fooditem(getattr(row, 'verbatimAssociatedTaxa'), part_of_organism)
        list_order = getattr(row, 'sequence')
        percentage = base_importer.possible_nan_to_zero(round(getattr(row, 'measurementValue', 0), 3))

        bj2, created = DietSetItem.objects.get_or_create(diet_set=obj, food_item=food_item, list_order=list_order, percentage=percentage)

        if created:
            return True
        else:
            return False

