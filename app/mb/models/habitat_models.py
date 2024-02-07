from django.db import models
from .base_model import BaseModel

class SourceHabitat(BaseModel):
    """
    Model representing a habitat associated with an Occurrence.
    """
    source_reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    habitat_type = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the Name of the Source Habitat"
        )
    habitat_percentage = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the Percentage of the Source Habitat"
        )
    
class MasterHabitat(BaseModel):
    pass

