from django.db import models
from .base_model import BaseModel

class SourceLocation(BaseModel):
    """
    Model representing a SourceLocation in MammalBase
    """
    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        blank=True,
        null=True
        )
    name = models.CharField(
        max_length=250,
        help_text="Enter the Name of the Source Location"
        )
    match_attempts = models.IntegerField(
        default=0,
        help_text="The number of attempted matches for this location."
        )
    verbatim_elevation = models.CharField(
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
        blank=True,
        null=True
        )
    name = models.CharField(
        max_length=250, 
        help_text="Enter the Name of the Master Location"
        )
    location_id = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the locationID of the Master Location"
        )
    higher_geography = models.ForeignKey(
        'self',
        null = True,
        blank = True,
        on_delete = models.CASCADE
        )
    is_reserve = models.BooleanField(
        default=False,
        help_text="Is this location a nature/wildlife/forest reserve?"
        )
    continent = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the continent of the Master Location"
        )
    country = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the country of the Master Location"
        )
    country_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Enter the country code of the Master Location"
        )
    state_province = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the state province of the Master Location"
        )
    county = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the county of the Master Location"
        )
    municipality = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the municipality of the Master Location"
        )
    locality = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the locality of the Master Location"
        )
    minimum_elevation_in_meters = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the minimum elevation in meters of the Master Location"
        )
    maximum_elevation_in_meters = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the maximum elevation in meters of the Master Location"
        )
    location_according_to = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the information about the source of this location information of the Master Location"
        )
    location_remarks = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the location remarks of the Master Location"
        )
    decimal_latitude = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the decimal latitude of the Master Location"
        )
    decimal_longitude = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the decimal longitude of the Master Location"
        )
    geodetic_datum = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text="Enter the geodetic datum of the Master Location"
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
    
class LocationRelation(BaseModel):
    source_location = models.ForeignKey('SourceLocation', on_delete=models.CASCADE)
    master_location = models.ForeignKey('MasterLocation', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('source_location', 'master_location',)

    def get_absolute_url(self):
        """
        Returns the url to access a particular Source Location instance.
        """
        return reverse('location-relation-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object
        """
        return '{0} ({1}) {2}'.format(self.source_location.name,self.master_location.name,self.master_location.reference)
