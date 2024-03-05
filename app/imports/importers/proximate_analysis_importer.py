from imports.importers.base_importer import BaseImporter
from ..tools import messages, possible_nan_to_none, possible_nan_to_zero
from mb.models.models import SourceAttribute, SourceReference, SourceEntity, SourceMethod, SourceUnit, ChoiceValue, SourceStatistic, SourceChoiceSetOption, SourceChoiceSetOptionValue, SourceMeasurementValue
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

        created = False
        
        if created:
            return True
        else:
            return False

ProximateAnalysisImporter = ProximateAnalysisImporter()
