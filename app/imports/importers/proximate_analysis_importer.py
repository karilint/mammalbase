from imports.importers.base_importer import BaseImporter
from mb.models.models import SourceAttribute, SourceReference, SourceEntity, SourceMethod, SourceUnit, ChoiceValue, SourceStatistic, SourceChoiceSetOption, SourceChoiceSetOptionValue, SourceMeasurementValue, ProximateAnalysis
from django.db import transaction
from django.contrib.auth.models import User
from mb.models.occurrence_models import Occurrence, Event
from mb.models.habitat_models import SourceHabitat
from decimal import Decimal

class ProximateAnalysisImporter(BaseImporter):

    def generate_standard_values_pa(self, items):
        standard_items = items
        remarks_text = "CP+EE+CF+NFE+ASH = 100"
        # Sum of reported values excluding dry matter and moisture
        item_sum = Decimal(0.0)
        for item in items.keys():
            if "reported" in item and "dm" not in item and "moisture" not in item and items[item] is not None:
                item_sum += Decimal(items[item])
        
        # If reported values sum to 1000 instead of 100 then divide sum by 10
        sum_to_thousand = False
        if abs(item_sum - Decimal(100)) > abs(item_sum - Decimal(1000)):
            sum_to_thousand = True
            remarks_text = "CP+EE+CF+NFE+ASH = 1000"
            item_sum /= Decimal(10)

        # If the sum of reported values is closer to 100 when moisture is included then add moisture to the sum
        if items["moisture_reported"] is not None:
            if sum_to_thousand and abs(Decimal(100) - (item_sum + (Decimal(items["moisture_reported"]) / Decimal(10)))) < abs(Decimal(100) - item_sum):
                item_sum += Decimal(items["moisture_reported"]) / Decimal(10)
                remarks_text = "Moisture+CP+EE+CF+NFE+ASH = 1000"
            elif abs(Decimal(100) - (item_sum + Decimal(items["moisture_reported"]))) < abs(Decimal(100) - item_sum):
                item_sum += Decimal(items["moisture_reported"])
                remarks_text = "Moisture+CP+EE+CF+NFE+ASH = 100"
        elif items["dm_reported"] is not None:
            if abs(item_sum - Decimal(items["dm_reported"])) < Decimal(0.001):
                remarks_text = "CP+EE+CF+NFE+ASH = DM"
        
        for item in list(items.keys()):
            if "reported" not in item or "dm" in item or "moisture" in item:
                continue
            elif items[item] is None:
                standard_items[item.replace("reported","std")] = None
            elif sum_to_thousand:
                standard_items[item.replace("reported","std")] = ((Decimal(items[item]) / Decimal(10)) / item_sum) * Decimal(100)
            else:
                standard_items[item.replace("reported","std")] = (Decimal(items[item]) / item_sum) * Decimal(100)

        standard_items["remarks"] = remarks_text
        standard_items["transformation"] = "Original value / (CP+EE+CF+ASH+NFE) * 100"
        
        return standard_items
    
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

