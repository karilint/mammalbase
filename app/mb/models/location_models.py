from django.db import models
from .base_model import BaseModel

class SourceLocation(BaseModel):
    """
    Model representing a SourceLocation in MammalBase
    """
    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    name = models.CharField(
        max_length=250,
        help_text="Enter the Name of the Source Location"
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
    
    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular Source Location instance.
        """
        return reverse('source-location-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s' % (self.name)


class MasterLocation(BaseModel):
    """
    Model representing a MasterLocation in MammalBase
    """
    reference = models.ForeignKey(
        'MasterReference',
        on_delete = models.CASCADE,
        )
    name = models.CharField(
        max_length=250, 
        help_text="Enter the Name of the Master Location"
        )
    tgn = models.PositiveSmallIntegerField(
        default=0, 
        blank=True,
        null=True, 
        help_text='Enter Thesaurus of Geographic Names id'
        )

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular Source Location instance.
        """
        return reverse('master-location-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s' % (self.name)
    

