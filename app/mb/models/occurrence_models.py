from django.db import models
from .base_model import BaseModel

class Occurrence(BaseModel):
    """
    Model representing a single occurrence of a taxon at a particular place
    at a particular time.
    """

    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE
        )
    event = models.ForeignKey(
        'Event',
        on_delete = models.CASCADE
        )
    location = models.ForeignKey(
        'SourceLocality',
        on_delete = models.CASCADE
        )
    verbatim_scientific_name = models.ForeignKey(
        'SourceEntity',
        on_delete= models.CASCADE
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
        help_text="References to other sources of information about the Occurrence."
        )

    
class Event(BaseModel):
    """
    Model representing an event that is associated with an Occurrence.
    """
    sampling_protocol = models.ForeignKey(
        'SourceMethod',
        blank=True,
        null=True,
        on_delete=models.CASCADE
        )
    habitat_type = models.ForeignKey(
        'SourceHabitat',
        blank=True,
        null=True,
        on_delete=models.CASCADE
        )
    verbatim_event_date = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="The verbatim original representation of the date and time information for an Event."
        )

class SourceLocality(BaseModel):
    """
    Model representing a location associated with an Occurrence.
    """
    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE
        )
    verbatim_locality = models.ForeignKey(
        'SourceLocation',
        on_delete=models.CASCADE
        )
    verbatim_eleveation = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="The original textual description of the verbatim elevation."
        )
    verbatim_longitude = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="The original textual description of the verbatim longitude."
        )
    verbatim_latitude = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="The original textual description of the verbatim latitude."
        )
    verbatim_depth = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="The original textual description of the verbatim depth."
        )
    verbatim_coordinate_system = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="The original textual description of the verbatim coordinate system."
        )
    verbatim_coordinates = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="The original textual description of the verbatim coordinates."
        )
    verbatim_srs = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="The original textual description of the verbatim spatial reference system."
        )

class SourceHabitat(BaseModel):
    """
    Model representing a habitat associated with an Occurrence.
    """
    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    name = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the Name of the Source Habitat"
        )
    habitatPercentage = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the Percentage of the Source Habitat"
        )
