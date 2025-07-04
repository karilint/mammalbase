""" mb.models.occurrence - 

This module should not be imported anywhere else than __init__.py!

To import models elsewhere use subpackage:
from mb.models import ModelName
"""

from django.db import models
from .base_model import BaseModel

class Occurrence(BaseModel):
    """
    Model representing a single occurrence of a taxon at a particular place
    at a particular time.
    """

    source_reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE
        )
    event = models.ForeignKey(
        'Event',
        on_delete = models.CASCADE,
        blank=True,
        null=True
        )
    source_location = models.ForeignKey(
        'SourceLocation',
        on_delete = models.CASCADE,
        default=None
        )
    source_entity = models.ForeignKey(
        'SourceEntity',
        on_delete=models.CASCADE,
        related_name='taxon_%(class)s',
        )
    organism_quantity = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="The number of organisms in the Occurrence."
        )
    organism_quantity_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="The type of the number of organisms in the Occurrence."
        )
    gender = models.ForeignKey(
        'ChoiceValue',
        on_delete = models.CASCADE,
        blank=True,
        null=True,
        related_name='gender_%(class)s',
        limit_choices_to={'choice_set':'Gender'}
        )
    life_stage = models.ForeignKey(
        'ChoiceValue',
        on_delete = models.SET_NULL,
        blank=True,
        null = True,
        related_name='life_stage_%(class)s',
        limit_choices_to={'choice_set': 'LifeStage'}
        )
    occurrence_remarks = models.TextField(
        blank=True,
        null=True,
        help_text="Comments or notes about the Occurrence."
        )
    associated_references = models.TextField(
        blank=True,
        null=True,
        help_text=(
                "References to other sources "
                "of information about the Occurrence.")
        )

class Event(BaseModel):
    """
    Model representing an event that is associated with an Occurrence.
    """
    source_method = models.ForeignKey(
        'SourceMethod',
        blank=True,
        null=True,
        on_delete=models.CASCADE
        )
    source_habitat = models.ForeignKey(
        'SourceHabitat',
        blank=True,
        null=True,
        on_delete=models.CASCADE
        )
    verbatim_event_date = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text=(
                "The verbatim original representation "
                "of the date and time information for an Event.")
        )
