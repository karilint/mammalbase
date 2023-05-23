from django.db import models
from mb.models import ProximateAnalysisItem
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class test(ProximateAnalysisItem):
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
