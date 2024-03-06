from imports.importers.base_importer import BaseImporter
from mb.models.models import SourceAttribute, SourceReference, SourceEntity, SourceMethod, SourceUnit, ChoiceValue, SourceStatistic, SourceChoiceSetOption, SourceChoiceSetOptionValue, SourceMeasurementValue, ProximateAnalysis
from django.db import transaction
from django.contrib.auth.models import User
from mb.models.occurrence_models import Occurrence, Event
from mb.models.habitat_models import SourceHabitat

class ProximateAnalysisImporter(BaseImporter):
    
    @transaction.atomic
    def importRow(self, row):
        """Put data of row to database.

        Args:
            row (Pandas): row of tsv
            importing_errors (list): list to possible errors

        Returns:
            bool: True if import is successded, otherwise False.
        """

        author = self.get_author(getattr(row, 'author'))
        source_reference = self.get_or_create_source_reference(getattr(row, 'references'), author)
        source_method = self.get_or_create_source_method(getattr(row, "measurementMethod"), source_reference, author)
        source_location = self.get_or_create_source_location(getattr(row, "verbatimLocality"), source_reference, author)
        
        obj, created = ProximateAnalysis.objects.get_or_create(method=source_method, reference=source_reference, location=source_location, cited_reference=str(getattr(row, "associatedReferences")), study_time=str(getattr(row, "verbatimEventDate"))) 
        
        if created:
            return True
        else:
            return False

