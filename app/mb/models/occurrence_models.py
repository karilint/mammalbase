from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from itis.models import TaxonomicUnits
from tdwg.models import Taxon as TdwgTaxon
from .base_model import BaseModel
from .models import SourceLocation, SourceReference

class Occurrence(BaseModel):
    """
    Model representing a single occurrence of a taxon at a particular place
    at a particular time.
    """

    reference_id = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    taxon_id = models.ForeignKey(
        'SourceEntity',
        on_delete=models.CASCADE,
        related_name='taxon_%(class)s'
        )
    organism_quantity = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="The number of organisms in the Occurrence.",
        )
    organism_quantity_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="The type of the number of organisms in the Occurrence.",
        )
    sex = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="The sex of the organism in the Occurrence.",
        )
    life_stage = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="The life stage of the organism in the Occurrence.",
        )
    occurrence_remarks = models.TextField(
        blank=True,
        null=True,
        help_text="Comments or notes about the Occurrence.",
        )
    associated_references = models.TextField(
        blank=True,
        null=True,
        help_text="References to other sources of information about the Occurrence.",
        )
