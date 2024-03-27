from django.db import transaction
from mb.models import DietSet, DietSetItem, Event, SourceHabitat
from .base_importer import BaseImporter
from mb.models import ChoiceValue

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
            part_of_organism, created = ChoiceValue.objects.get_or_create(choice_set="FoodItemPart", caption=part_of_organism.capitalize())
                
        
        print("Creating diet set")
        obj, created = DietSet.objects.get_or_create(reference=reference, cited_reference=getattr(row, 'associatedReferences'), taxon=taxon, location=new_source_location, sample_size=getattr(row, 'individualCount'),
                                                     time_period=time_period, method=method, study_time=getattr(row, 'verbatimEventDate'), created_by=author)

        if created:
            self.create_diet_set_item(row, obj)
            return True
        else:
            return False

    def create_diet_set_item(self, row, diet_set: DietSet):
        """
        Creates a DietSetItem object from a row of data and a DietSet object.
        """
        food_item = self.get_food_item(getattr(row, 'PartOfOrganism'))
        list_order = getattr(row, 'sequence')
        percentage = round((getattr(row, 'measurementValue')), 3)

        obj, created = DietSetItem.objects.get_or_create(diet_set=diet_set, food_item=food_item, list_order=list_order)

        if created:
            return True
        else:
            return False
