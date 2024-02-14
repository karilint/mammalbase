from django.db import models
from .base_model import BaseModel

class SourceHabitat(BaseModel):
    """
    Model representing a habitat associated with an Occurrence.
    """
    master_habitat = models.ManyToManyField(
        'MasterHabitat',
        through='HabitatRelation',
        through_fields=('source_habitat', 'master_habitat')
    )
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
    reference = models.ForeignKey(
        'MasterReference',
        on_delete = models.CASCADE,
        )
    parent = models.ForeignKey(
        'self',
        null = True,
        blank = True,
        on_delete = models.CASCADE
    )
    source_habitat = models.ManyToManyField(
        'SourceHabitat',
        )
    name = models.CharField(
        max_length=250,
        help_text="Enter the Name of the Master Habitat"
        )
    eco_code = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text='Enter the eco code of the Master Habitat'
        )
    biome_code = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text='Enter the biome code of the Master Habitat'
        )
    
    class Meta:
      ordering = ['name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular Source Habitat instance.
        """
        return reverse('master-habitat-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s' % (self.name)
    

class HabitatRelation(BaseModel):
    source_habitat = models.ForeignKey('SourceHabitat', on_delete=models.CASCADE)
    master_habitat = models.ForeignKey('MasterHabitat', on_delete=models.CASCADE)

    class Meta:
      unique_together = ('source_habitat', 'master_habitat',)

    def get_absolute_url(self):
        """
        Returns the url to access a particular Source Habitat instance.
        """
        return reverse('attribute-relation-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object
        """
        return '{0} ({1}) {2}'.format(self.source_habitat.habitat_type,self.master_habitat.name,self.master_habitat.reference)
