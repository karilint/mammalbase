""" mb.models.proximate_analysis - ProximateAnalysis and related Models

This module should not be imported anywhere else than __init__.py!

To import models elsewhere use subpackage:
from mb.models import ModelName
"""

from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from itis.models import TaxonomicUnits
from .base_model import BaseModel

class ProximateAnalysis(BaseModel):
    """
    Model representing a ProximateAnalysis in MammalBase
    """

    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    location = models.ForeignKey(
        'SourceLocation',
        on_delete=models.CASCADE,
        blank=True,
        null = True,
        )
    cited_reference = models.CharField(
        blank=True,
        null=True,
        max_length=250,
        help_text="Enter the original reference, if not this study."
    )
    method = models.ForeignKey(
        'SourceMethod',
        on_delete=models.CASCADE,
        null = True,
        )
    study_time = models.CharField(
        blank=True,
        null=True,
        max_length=250,
        help_text="Enter the time when this study was performed."
    )

    class Meta:
        ordering = ['reference']

    def get_absolute_url(self):
        """
        Returns the url to access a particular ProximateAnalysis instance.
        """
        return reverse('proximate-analysis-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.reference}"

class ProximateAnalysisItem(BaseModel):
    """
    Model representing a ProximateAnalysisItem in MammalBase
    """

    proximate_analysis = models.ForeignKey(
        'ProximateAnalysis',
        on_delete = models.CASCADE,
    )
    forage = models.ForeignKey(
        'FoodItem',
        on_delete = models.CASCADE,
    )
    location = models.ForeignKey(
        'SourceLocation',
        on_delete=models.CASCADE,
        blank = True,
        null = True,
    )
    cited_reference = models.CharField(
        blank = True,
        null=True,
        max_length=250,
        help_text="Enter the original reference, if not this study."
    )
    sample_size = models.PositiveSmallIntegerField(
        blank = True,
        null=True,
        default=0,
        help_text='Sample size'
    )
    dm_reported = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    moisture_reported = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    cp_reported = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    ee_reported = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    cf_reported = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    ash_reported = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    nfe_reported = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    total_carbohydrates_reported = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    cp_std = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    ee_std = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    cf_std = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    ash_std = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    nfe_std = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    transformation = models.CharField(
        blank = True,
        null=True,
        max_length=250
    )
    remarks = models.CharField(
        blank = True,
        null=True,
        max_length=250,
        help_text="Enter remarks."
    )

    #new fields below
    measurement_determined_by = models.CharField(
        blank = True,
        null=True,
        max_length=250
    )
    measurement_remarks = models.CharField(
        blank = True,
        null=True,
        max_length=250
    )
    #moisture
    moisture_dispersion = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    moisture_measurement_method = models.CharField(
        blank = True,
        null=True,
        max_length=250
    )
    #dry_matter
    dm_dispersion = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    dm_measurement_method = models.CharField(
        blank = True,
        null=True,
        max_length=250
    )
    #ether_extract
    ee_dispersion = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)])
    ee_measurement_method = models.CharField(
        blank = True,
        null=True,
        max_length=250
    )
    #crude_protein
    cp_dispersion = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    cp_measurement_method = models.CharField(
        blank = True,
        null=True,
        max_length=250
    )
    #crude_fiber
    cf_dispersion = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    cf_measurement_method = models.CharField(
        blank = True,
        null=True,
        max_length=250
    )
    #ash
    ash_dispersion = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    ash_measurement_method = models.CharField(
        blank = True,
        null=True,
        max_length=250
    )
    #nitrogen_free_extract
    nfe_dispersion = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    nfe_measurement_method = models.CharField(
        blank = True,
        null=True,
        max_length=250
    )

    class Meta:
        ordering = ['proximate_analysis','forage']

    def get_absolute_url(self):
        """
        Returns the url to access a particular ProximateAnalysisItem instance.
        """
        return reverse('proximate-analysis-item-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.proximate_analysis} - {self.forage} "

# https://resources.rescale.com/using-database-views-in-django-orm/
class ViewProximateAnalysisTable(models.Model):
    """
    Model representing a ProximateAnalysis results as a MySQL view in MammalBase
    """
    id = models.BigIntegerField(primary_key=True)
    tsn = models.ForeignKey(
        TaxonomicUnits,
        to_field="tsn",
        db_column="tsn",
        on_delete=models.DO_NOTHING
    )
    part = models.CharField(max_length=200)
    cp_std = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7)
    ee_std = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7)
    cf_std = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7)
    ash_std = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7
    )
    nfe_std = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7
    )
    reference_ids = models.CharField(max_length=200)
    n_taxa = models.PositiveSmallIntegerField()
    n_reference = models.PositiveSmallIntegerField()
    n_analysis = models.PositiveSmallIntegerField()

    class Meta:
        managed = False
        db_table = 'mb_view_pa_table'
        ordering = ['part','tsn__hierarchy']

    def get_absolute_url(self):
        """
        Returns the url to access a particular ProximateAnalysisTable instance.
        """
        return reverse('view-proximate-analysis-table-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.tsn}"
