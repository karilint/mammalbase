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

        print("row: " + str(row))
        author = self.get_author(getattr(row, 'author'))
        """
        attribute_dict = {
            "reference" : get_sourcereference_citation(getattr(row, 'references'), author),
            "method" : None,
            "location" : None,
            "study_time" : None,
            "cited_reference" : None
        }
        """
        source_reference = self.get_or_create_source_reference(getattr(row, 'references'), author)
        source_method = self.get_or_create_source_method(getattr(row, "measurementMethod"), source_reference, author)
        source_location = self.get_or_create_source_location(getattr(row, "verbatimLocality"), source_reference, author)
        study_time = getattr(row, "verbatimEventDate")
        cited_reference = getattr(row, "associatedReferences")

        """
        pa = None
        pa_old = ProximateAnalysis.objects.filter(**attribute_dict)
        if len(pa_old) > 0:
            pa = pa_old[0]
        else:
            pa = ProximateAnalysis(**attribute_dict)
            pa.save()
        create_proximate_analysis_item(row, pa, attribute_dict["location"], attribute_dict["cited_reference"], headers)
        """

        created = True
        
        if created:
            return True
        else:
            return False

ProximateAnalysisImport = ProximateAnalysisImporter()
