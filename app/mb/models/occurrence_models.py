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
    event_id = models.ForeignKey(
        'OccurrenceEvent',
        on_delete = models.CASCADE
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
    # check accepted values
    sex = models.ForeignKey(
        'ChoiceValue',
        on_delete = models.CASCADE,
        blank=True,
        null=True,
        limit_choices_to={'choice_set':'Sex'}
        )
    # check accepted values
    life_stage = models.ForeignKey(
        'ChoiceValue',
        on_delete = models.SET_NULL,
        blank=True,
        null = True,
        limit_choices_to={'choice_set': 'LifeStage'}
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

    
class OccurrenceEvent(BaseModel):
    """
    Model representing an event that is associated with an Occurrence.
    """
    sampling_protocol = models.TextField(
        blank=True,
        null=True,
        help_text="The name of, reference to, or description of the method or protocol used during an Event.",
        )
    verbatim_event_date = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="The verbatim original representation of the date and time information for an Event.",
        )

# source_locality ?
class OccurrenceLocation(BaseModel):
    """
    Model representing a location associated with an Occurrence.
    """
    verbatim_locality = models.ForeignKey(
        'SourceLocation',
        on_delete=models.CASCADE,
        )
    verbatim_eleveation = models.CharField(
        blank=True,
        null=True,
        help_text="The original textual description of the verbatim elevation."
    )
    verbatim_longitude = models.CharField(
        blank=True,
        null=True,
        help_text="The original textual description of the verbatim longitude."
    )
    verbatim_latitude = models.CharField(
        blank=True,
        null=True,
        help_text="The original textual description of the verbatim latitude."
    )
    verbatim_depth = models.CharField(
        blank=True,
        null=True,
        help_text="The original textual description of the verbatim depth."
    )
    verbatim_coordinate_system = models.CharField(
        blank=True,
        null=True,
        help_text="The original textual description of the verbatim coordinate system."
    )
    verbatim_srs = models.CharField(
        blank=True,
        null=True,
        help_text="The original textual description of the verbatim spatial reference system."
    )
