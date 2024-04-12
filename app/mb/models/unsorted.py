""" mb.models.unsorted - Models that won't fit any other file.

Ideally this module should not exist.

Do not add any new models here.

This module should not be imported anywhere else than __init__.py!

To import models elsewhere use subpackage:
from mb.models import ModelName
"""

from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from itis.models import TaxonomicUnits
from tdwg.models import Taxon as TdwgTaxon
from .base_model import BaseModel
from .validators import validate_doi
from .proximate_analysis import ViewProximateAnalysisTable


class AttributeRelation(BaseModel):
    source_attribute = (
            models.ForeignKey('SourceAttribute', on_delete=models.CASCADE))
    master_attribute = (
            models.ForeignKey('MasterAttribute', on_delete=models.CASCADE))
    remarks = models.TextField(
            blank=True,
            null=True,
            max_length=500,
            help_text="Enter remarks for the Attribute Relation")

    class Meta:
        unique_together = ('source_attribute', 'master_attribute',)

    def get_absolute_url(self):
        """
        Returns the url to access a particular AttributeRelation instance.
        """
        return reverse('attribute-relation-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object
        """
        return (
                f"{self.source_attribute.name} "
                f"({self.master_attribute.name}) "
                f"{self.master_attribute.reference}")


class ChoiceValue(BaseModel):
    """
    Model representing a ChoiceValue in MammalBase
    """

    choice_set = models.CharField(
            max_length=25,
            help_text="Enter the Choice Set of the ChoiceValue")
    caption = models.CharField(
            max_length=25,
            help_text="Enter the Caption of the ChoiceValue")
#    link = models.URLField(
#            max_length=200,
#            help_text="Enter a valid URL for the Source Reference",
#            blank=True,
#            null=True)

    class Meta:
        ordering = ['choice_set','caption']
        unique_together = ('choice_set','caption',)

    def get_absolute_url(self):
        """
        Returns the url to access a particular ChoiceValue instance.
        """
        return reverse('choice-value-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.choice_set} - {self.caption} "

class ChoiceSetOptionRelation(BaseModel):
    source_choiceset_option = models.ForeignKey(
            'SourceChoiceSetOption',
            on_delete=models.CASCADE)
    master_choiceset_option = models.ForeignKey(
            'MasterChoiceSetOption',
            on_delete=models.CASCADE)
    remarks = models.TextField(
            blank=True,
            null=True,
            max_length=500,
            help_text="Enter remarks for the ChoiceSetOption Relation")

    class Meta:
        unique_together = (
                'source_choiceset_option',
                'master_choiceset_option')

    def get_absolute_url(self):
        """
        Returns the url to access a particular ChoiceSetOptionRelation instance.
        """
        return reverse(
                'choiceset_option-relation-detail',
                args = [str(self.id)])

    def __str__(self):
        """
        String for representing the Model object
        """
        return (
                f"{self.source_choiceset_option.name} - "
                f"{self.master_choiceset_option.name}")


class EntityClass(BaseModel):
    """
    Model representing a Entity Class in MammalBase
    """

    name = models.CharField(
            max_length=50,
            help_text="Enter the Name of the Entity Class")
#    link = models.URLField(
#            max_length=200,
#            help_text="Enter a valid URL for the Source Reference",
#            blank=True,
#            null=True)

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular Entity Class instance.
        """
        return reverse('entity-class-detail', args = [str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.name}"


class RelationClass(BaseModel):
    """
    Model representing a RelationClass in MammalBase
    """

    name = models.CharField(
            max_length=25,
            help_text="Enter the Name of the RelationClass")

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular RelationClass instance.
        """
        return reverse('relation-class-detail', args = [str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.name}"


class FoodItem(BaseModel):
    """
    Model representing a FoodItem in MammalBase
    """
    name = models.CharField(
            max_length=250,
            unique=True,
            help_text="Enter the Name of the FoodItem")
    part = models.ForeignKey(
            'ChoiceValue',
            on_delete = models.SET_NULL,
            null = True,
            limit_choices_to={'choice_set': 'FoodItemPart'})
    tsn = models.ForeignKey(
            TaxonomicUnits,
            to_field="tsn",
            db_column="tsn",
            blank=True,
            null=True,
            on_delete = models.SET_NULL,
            related_name='tsn_food')
    pa_tsn = models.ForeignKey(
            TaxonomicUnits,
            to_field="tsn",
            db_column="pa_tsn",
            blank=True,
            null=True,
            on_delete = models.SET_NULL,
            related_name='tsn_pa')
    is_cultivar = models.BooleanField(
            default=False,
            help_text='Is this Food Item a FAO cultivar?')

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular FoodItem instance.
        """
        return reverse('food-item-detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        if self.tsn is None:
            super().save(*args, **kwargs)  # Call the "real" save() method.
        else:
            tsn = get_object_or_404(TaxonomicUnits, tsn=self.tsn.tsn)
            if tsn is not None:
                tsn_hierarchy = tsn.hierarchy_string.split("-")
                i=len(tsn_hierarchy)-1
                if self.part is not None:
                    while i>=0 :
                        part=self.part.caption
                        if part=='CARRION':
                            part='WHOLE'
                        pa = ViewProximateAnalysisTable.objects.filter(
                            tsn__hierarchy_string__endswith=tsn_hierarchy[i]).filter(
                                part__exact=part)
                        if len(pa)==1:
                            self.pa_tsn=pa.all()[0].tsn
                            break
                        i=i-1
            super().save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.name}"

class MasterAttributeGroup(BaseModel):
    name = models.CharField(
            max_length=250,
            help_text="Enter the Name of the Master Attribute Group")
    remarks = models.TextField(
            blank=True,
            null=True,
            max_length=500,
            help_text="Enter remarks for the Master Attribute Group")

    class Meta:
        ordering = ['name']

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.name}"

class AttributeGroupRelation(BaseModel):
    group = models.ForeignKey('MasterAttributeGroup', on_delete=models.CASCADE)
    attribute = models.ForeignKey('MasterAttribute', on_delete=models.CASCADE)
    display_order = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['group__name', 'display_order']

    def __str__(self):
        return f'{self.group.name} - {self.attribute.name}'

class MasterAttribute(BaseModel):
    """
    Model representing a MasterAttribute in MammalBase
    """
    # valueType choices from ETS: https://ecologicaltraitdata.github.io/ETS/
    TYPE = [
        ('numeric', 'numeric'),
        ('integer', 'integer'),
        ('categorical', 'categorical'),
        ('ordinal', 'ordinal'),
        ('logical', 'logical'),
        ('character', 'character'),
    ]

    reference = models.ForeignKey(
            'MasterReference',
            on_delete = models.CASCADE)
    entity = models.ForeignKey(
            'EntityClass',
            on_delete = models.CASCADE)
    source_attribute = models.ManyToManyField(
            'SourceAttribute',
            through='AttributeRelation',
            through_fields=('master_attribute', 'source_attribute') )
    name = models.CharField(
            max_length=250,
            help_text="Enter the Name of the Master Attribute")
    unit = models.ForeignKey(
            'MasterUnit',
            blank=True,
            null=True,
            on_delete = models.CASCADE)

    min_allowed_value = models.CharField(
            blank=True,
            null=True,
            max_length=25,
            help_text="Enter minimum value for the Master Attribute")
    max_allowed_value = models.CharField(
            blank=True,
            null=True,
            max_length=25,
            help_text="Enter maximum value for the Master Attribute")
    description = models.TextField(
            blank=True,
            null=True,
            max_length=500,
            help_text="Enter description for the Master Attribute")
    remarks = models.TextField(
            blank=True,
            null=True,
            max_length=500,
            help_text="Enter remarks for the Master Attribute")
    # Add description-field
    groups = models.ManyToManyField(
            'MasterAttributeGroup',
            through='AttributeGroupRelation')

    value_type = models.CharField(
            max_length=25,
            choices=TYPE,
            default='character',
            help_text='Select the valueType of the MasterAttribute')


    class Meta:
        ordering = ['entity__name','name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular Master Attribute instance.
        """
        return reverse('master-attribute-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        if self.unit:
            return (
                    f"{self.entity.name}: "
                    f"{self.name} "
                    f"({self.unit.print_name})")
        return f"{self.entity.name}: {self.name}"

class MasterChoiceSetOption(BaseModel):
    """
    Model representing a MasterChoiceSetOption in MammalBase
    """
    master_attribute = models.ForeignKey(
            'MasterAttribute',
            on_delete = models.CASCADE)
    source_choiceset_option = models.ManyToManyField(
            'SourceChoiceSetOption',
            through = 'ChoiceSetOptionRelation',
            through_fields = (
                'master_choiceset_option',
                'source_choiceset_option'
            ) )
    display_order = models.PositiveSmallIntegerField(
            default=10,
            help_text='Display order on choises')
    name = models.CharField(
            max_length=250,
            help_text="Enter the Name of the Master Attribute")
    description = models.TextField(
            blank=True,
            null=True,
            max_length=1500,
            help_text="Enter description for the Master Choice Set Option")

    class Meta:
        ordering = ['master_attribute__name', 'display_order']

    def get_absolute_url(self):
        """
        Returns the url to access a particular MasterChoiceSetOption instance.
        """
        return reverse('master-choiceset-option', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.master_attribute.name} - {self.name} "


class MasterEntity(BaseModel):
    """
    Model representing a MasterEntity in MammalBase
    """
    reference = models.ForeignKey(
            'MasterReference',
            on_delete = models.CASCADE
    )
    entity = models.ForeignKey(
            'EntityClass',
            on_delete = models.CASCADE
    )
    source_entity = models.ManyToManyField(
            'SourceEntity',
            through = 'EntityRelation',
            through_fields = ('master_entity', 'source_entity')
    )
    name = models.CharField(
            max_length=250,
            help_text="Enter the Name of the Master Entity"
    )
    taxon = models.ForeignKey(
            TdwgTaxon,
            on_delete = models.SET_NULL,
            null = True,
            blank = True,
            related_name = 'master_entities',
            help_text = "The associated taxon (optional)"
    )

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular Master Entity instance.
        """
        return reverse('master-entity-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.name}"

class MasterReference(BaseModel):
    """
    Model representing a Standard Reference in MammalBase
    """
    # Choices from here: https://github.com/greenelab/scihub/issues/7
    TYPE = [
        ('book', 'book'),
        ('book-chapter', 'book-chapter'),
        ('book-part', 'book-part'),
        ('book-section', 'book-section'),
        ('book-series', 'book-series'),
        ('book-set', 'book-set'),
        ('book-track', 'book-track'),
        ('component', 'component'),
        ('dataset', 'dataset'),
        ('dissertation', 'dissertation'),
        ('edited-book', 'edited-book'),
        ('journal', 'journal'),
        ('journal-article', 'journal-article'),
        ('journal-issue', 'journal-issue'),
        ('journal-volume', 'journal-volume'),
        ('monograph', 'monograph'),
        ('other', 'other'),
        ('posted-content', 'posted-content'),
        ('proceedings', 'proceedings'),
        ('proceedings-article', 'proceedings-article'),
        ('reference-book', 'reference-book'),
        ('reference-entry', 'reference-entry'),
        ('report', 'report'),
        ('report-series', 'report-series'),
        ('standard', 'standard'),
        ('standard-series', 'standard-series'),
    ]
    type = models.CharField(
            max_length=25,
            choices=TYPE,
            default='other',
            help_text='Select the type of the Standard Reference',
            blank=True,
            null=True)
    doi = models.CharField(
            max_length=100,
            validators=[validate_doi],
            help_text=(
                    "Enter the DOI number that begins "
                    "with 10 followed by a period"),
            blank=True,
            null=True,)
    uri = models.URLField(
            max_length=200,
            help_text="Enter the Uniform Resource Identifier link",
            blank=True,
            null=True,)
    first_author = models.CharField(
            max_length=50,
            help_text=(
                    "Enter the name of the first author of "
                    "the Standard Reference"),
            blank=True,
            null=True)
    year = models.IntegerField(
            validators=[MinValueValidator(1800),
            MaxValueValidator(2100)],
            blank=True,
            null=True,)
    title = models.CharField(
            max_length=400,
            help_text="Enter the Title of the Standard Reference",
            blank=True,
            null=True,)
    container_title = models.CharField(
            max_length=100,
            help_text="Enter the Container Title of the Standard Reference",
            blank=True,
            null=True,)
    volume = models.IntegerField(
            validators=[MinValueValidator(0),
            MaxValueValidator(4000)],
            blank=True,
            null=True,)
    issue = models.CharField(
            max_length=5,
            help_text="Enter the Issue of the Standard Reference",
            blank=True,
            null=True,)
    page = models.CharField(
            max_length=50,
            help_text="Enter the Page(s) of the Standard Reference",
            blank=True,
            null=True,)
    citation = models.CharField(
            max_length=500,
            help_text="Enter the Citation of the Standard Reference")
#    link = models.URLField(
#            max_length=200,
#            help_text="Enter a valid URL for the Source Reference",
#            blank=True,
#            null=True,)
    is_public = models.BooleanField(
            help_text="Enter if the source is public",
            blank=False,
            null=True,)

    class Meta:
        ordering = ['citation']

    def get_absolute_url(self):
        """
        Returns the url to access a particular reference instance.
        """
        return reverse('master-reference-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.citation}"

class MasterUnit(BaseModel):
    """
    Model representing a MasterUnit in MammalBase
    """
    source_unit = models.ManyToManyField(
        'SourceUnit'
    )
    name = models.CharField(
        max_length=25, help_text="Enter the name of the Master Unit")
    print_name = models.CharField(
        max_length=25, help_text="Enter the Print value of the name of a Master Unit")
    quantity_type = models.CharField(
        max_length=25, help_text="Enter the Quantity type of the Master Unit")
    unit_value = models.DecimalField(
                         max_digits = 19,
                         decimal_places = 10)
    remarks = models.TextField(
        blank=True, null=True, max_length=500, help_text="Enter remarks for the Master Unit")

    class Meta:
        ordering = ['quantity_type','unit_value']

    def get_absolute_url(self):
        """
        Returns the url to access a particular Master Unit instance.
        """
        return reverse('master-unit-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return (
                f"{self.quantity_type}: "
                f"{self.name} "
                f"({self.print_name})")

class SourceAttribute(BaseModel):
    """
    Model representing a SourceAttribute in MammalBase
    """
    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    entity = models.ForeignKey(
        'EntityClass',
        on_delete = models.CASCADE,
        )
    master_attribute = models.ManyToManyField(
        'MasterAttribute',
        through='AttributeRelation',
        through_fields=('source_attribute', 'master_attribute')
    )
    name = models.CharField(max_length=250, help_text="Enter the Name of the Attribute")
    TYPE = (
        (0, 'Not Specified'),
        (1, 'Numerical variable'),
        (2, 'Categorical variable'),
    )
    type = models.PositiveSmallIntegerField(
        choices=TYPE, default=3, help_text='Select the type of the Attribute')
    remarks = models.TextField(
        blank=True, null=True, max_length=500, help_text="Enter remarks for the Attribute")
    method = models.ForeignKey(
        'SourceMethod',
        on_delete=models.CASCADE,
        blank=True,
        null = True,
        related_name='method_%(class)s',
        )

    class Meta:
        ordering = ['entity__name','name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular Source Attribute instance.
        """
        return reverse('source-attribute-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.entity.name} - {self.name} "


class SourceChoiceSetOption(BaseModel):
    """
    Model representing a SourceChoiceSetOption in MammalBase
    """
    source_attribute = models.ForeignKey(
        'SourceAttribute',
        on_delete = models.CASCADE,
        )
    master_choiceset_option = models.ManyToManyField(
        'MasterChoiceSetOption',
        through='ChoiceSetOptionRelation',
        through_fields=('source_choiceset_option', 'master_choiceset_option')
    )
    display_order = models.PositiveSmallIntegerField(
        default=10, help_text='Display order on choises'
    )
    name = models.CharField(max_length=250, help_text="Enter the Source Choice Set Option")
    description = models.TextField(
        blank=True, null=True, max_length=500,
        help_text="Enter the description for the Source Choice Set Option"
    )

    class Meta:
        ordering = ['source_attribute__name','display_order']

    def get_absolute_url(self):
        """
        Returns the url to access a particular SourceChoiceSetOption instance.
        """
        return reverse('source-choiceset-option', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.source_attribute.name} - {self.name} "

class SourceChoiceSetOptionValue(BaseModel):
    """
    Model representing a SourceChoiceSetOptionValue in MammalBase
    """
    source_entity = models.ForeignKey(
        'SourceEntity',
        on_delete = models.CASCADE,
        )
    source_choiceset_option = models.ForeignKey(
        'SourceChoiceSetOption',
        on_delete = models.CASCADE,
        )

    class Meta:
        ordering = ['source_entity__name','source_choiceset_option__display_order']

    def get_absolute_url(self):
        """
        Returns the url to access a particular SourceChoiceSetOptionValue instance.
        """
        return reverse('source-choiceset-option-value', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return (
                f"{self.source_choiceset_option.source_attribute.name} - "
                f"{self.source_choiceset_option.name} ")

class SourceEntity(BaseModel):
    """
    Model representing a SourceEntity in MammalBase
    """
    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    entity = models.ForeignKey(
        'EntityClass',
        on_delete = models.CASCADE,
        )
    master_entity = models.ManyToManyField(
        'MasterEntity',
        through='EntityRelation',
        through_fields=('source_entity', 'master_entity')
        )
    name = models.CharField(
        max_length=250,
        help_text="Enter the Name of the Source Entity"
        )

    taxon = models.ForeignKey(
        TdwgTaxon,
        blank=True,
        null=True,
        on_delete= models.CASCADE,
        )

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular Source Entity instance.
        """
        return reverse('source-entity-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.name}"

class SourceMeasurementValue(BaseModel):
    """
    Model representing a SourceMeasurementValue in MammalBase
    """
    source_entity = models.ForeignKey(
        'SourceEntity',
        on_delete = models.CASCADE,
        )
    source_attribute = models.ForeignKey(
        'SourceAttribute',
        on_delete = models.CASCADE,
        )
    source_location = models.ForeignKey(
        'SourceLocation',
        on_delete = models.CASCADE,
        null=True,
        blank=True,
        default = None
        )
    n_total = models.PositiveSmallIntegerField(
        default=0, blank=True, null=True, help_text='n for total number of specimens measured.'
    )
    n_unknown = models.PositiveSmallIntegerField(
        default=0, blank=True, null=True,
        help_text='n for total number of unknown gender specimens measured.'
    )
    n_male = models.PositiveSmallIntegerField(
        default=0, blank=True, null=True, help_text='n for total number of male specimens measured.'
    )
    n_female = models.PositiveSmallIntegerField(
        default=0,
        blank=True,
        null=True,
        help_text='n for total number of female specimens measured.'
    )
    minimum = models.DecimalField(
        max_digits=19, decimal_places=10, help_text='Minimum measurement value reported.'
    )
    maximum = models.DecimalField(
        max_digits=19, decimal_places=10, help_text='Maximum measurement value reported.'
    )
    mean = models.DecimalField(
        max_digits=19, decimal_places=10, help_text='Mean of measurement values reported.'
    )
    std = models.DecimalField(
        max_digits=19,
        decimal_places=10,
        default=None,
        blank=True,
        null=True,
        help_text='Standard deviation of measurement values reported.'
    )
    source_statistic = models.ForeignKey(
        'SourceStatistic',
        null=True, blank=True,
        on_delete = models.SET_NULL,
        )
    source_unit = models.ForeignKey(
        'SourceUnit',
        null=True, blank=True,
        on_delete = models.SET_NULL,
        )
    gender = models.ForeignKey(
        'ChoiceValue',
        on_delete = models.SET_NULL,
        blank=True,
        null = True,
        limit_choices_to={'choice_set': 'Gender'},
        related_name='gender%(class)s',
        )
    life_stage = models.ForeignKey(
        'ChoiceValue',
        on_delete = models.SET_NULL,
        blank=True,
        null = True,
        limit_choices_to={'choice_set': 'LifeStage'},
        related_name='lifestage%(class)s',
        )
    measurement_accuracy = models.TextField(
        blank=True,
        null=True,
        max_length=50,
        help_text="The description of the potential error associated with the measurementValue."
    )
    measured_by = models.TextField(
        blank=True,
        null=True,
        max_length=100,
        help_text=("A list (concatenated and separated) of names of people, groups, "
                   "or organizations who determined the value of the measurement. "
                   "The recommended best practice is to separate the values "
                   "with a vertical bar (' | ')."
        )
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text="Enter remarks for the Source Measurement"
    )
    data_quality_score = models.SmallIntegerField(
        blank=True,
        null=True,
        default=0,
        help_text="Data quality score for the data"
    )
    # unit is no longer in use - to be deleted
    cited_reference = models.CharField(
        blank=True,
        null=True,
        max_length=1000,
        help_text=("Enter the original reference, if not this study. "
                   "If original, enter 'Original study'."
        )
        )
    unit = models.CharField(
        null=True,
        blank=True,
        max_length=250, help_text='Measurement unit reported.')

    def clean(self):
        # Don't allow wrong n values.
        if self.n_total != self.n_unknown + self.n_male + self.n_female:
            raise ValidationError(gettext_lazy(
                    'n total needs to be sum of all n fields.'))
        if self.minimum > self.maximum:
            raise ValidationError(gettext_lazy(
                    'Measurement error: min > max.'))
        if self.mean < self.minimum or self.mean > self.maximum :
            raise ValidationError(gettext_lazy(
                    'Measurement error: mean outside min or max.'))
        if self.n_total in (0, 1):
            self.std = None
        if self.std is not None and self.std > self.maximum - self.minimum:
            raise ValidationError(gettext_lazy(
                    'Measurement error: std is too large.'))

    class Meta:
        ordering = ['source_attribute__name', '-n_total']

    def get_absolute_url(self):
        """
        Returns the url to access a particular SourceMeasurementValue instance.
        """
        return reverse('source-measurement-value', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.source_attribute.name}: {str(self.n_total)} "

    # Used to calculate the quality of the measurement data
    def calculate_data_quality_score_for_measurement(self):
        score = 0
        #1 weight of taxon quality
        taxon = self.source_entity.entity.name
        if taxon in ('Species', 'Subspecies'):
            score += 1

        #2 weight of having a reported citation of the data
        citation = self.cited_reference
        if citation == 'Original study':
            score += 2
        elif citation is not None:
            score += 1

        #3 weight of source quality in the diet
        try:
            source_type = self.source_entity.reference.master_reference.type
        except:
            score += 0
        else:
            if source_type == 'journal-article':
                score += 3
            elif source_type == 'book':
                score += 2
            elif source_type == 'data set':
                score += 1

        #4 weight of having a described method in the method
        if self.source_attribute.method:
            score += 1

        #5 weight of having individual count
        if self.n_total != 0:
            score += 1

        #6 weight of having minimum and maximum
        if self.minimum != 0 and self.maximum != 0:
            score += 1

        #7 weight of having Standard Deviation
        if self.std != 0:
            score += 1

        return score

class SourceMethod(BaseModel):
    """
    Model representing a Source Method in MammalBase
    """

    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    name = models.CharField(
        max_length=500,
        help_text="Enter the method described in the Reference"
    )

    class Meta:
        ordering = ['name']
        unique_together = ('reference','name')

    def get_absolute_url(self):
        """
        Returns the url to access a particular Source Method.
        """
        return reverse('source-method-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.name}"

class SourceStatistic(BaseModel):
    """
    Model representing a Source Statistic in MammalBase
    """

    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    name = models.CharField(
        max_length=500,
        help_text="Enter the statistic described in the Reference"
    )

    class Meta:
        ordering = ['name']
        unique_together = ('reference','name')

    def get_absolute_url(self):
        """
        Returns the url to access a particular Source Statistic.
        """
        return reverse('source-statistic-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.name}"

class SourceUnit(BaseModel):
    """
    Model representing a SourceUnit in MammalBase
    """
    master_unit = models.ManyToManyField(
        'MasterUnit',
        through='UnitRelation',
        through_fields=('source_unit', 'master_unit')
    )
    name = models.CharField(
        max_length=25,
        help_text="Enter the name of the Source Unit"
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text="Enter remarks for the Source Unit"
    )

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular Source Unit instance.
        """
        return reverse('source-unit-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.name}"

class EntityRelation(BaseModel):
    source_entity = models.ForeignKey('SourceEntity', on_delete=models.CASCADE)
    master_entity = models.ForeignKey('MasterEntity', on_delete=models.CASCADE)
    relation = models.ForeignKey('RelationClass',on_delete = models.CASCADE)
    relation_status = models.ForeignKey(
        'MasterChoiceSetOption',
        on_delete = models.SET_NULL,
        null = True,
        related_name='relationstatus%(class)s')
    data_status = models.ForeignKey(
        'MasterChoiceSetOption',
        on_delete = models.SET_NULL,
        null = True,
        limit_choices_to={'master_attribute__name': 'Verification'},
        related_name='datastatus%(class)s',
        )
    remarks = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text="Enter remarks for the Entity Relation"
    )

    class Meta:
        unique_together = ('source_entity', 'master_entity','relation')

    # FIX: What is this? Is this needed? Gives error. Comminting out now.
    #def level_1(self):
    #    return self.name_one.qualifier.level

    def get_absolute_url(self):
        """
        Returns the url to access a particular EntityRelation instance.
        """
        return reverse('entity-relation-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object
        """
        return (
                f"{self.source_entity.name} "
                f"({self.master_entity.name}) "
                f"{self.master_entity.reference}")

class SourceReference(BaseModel):
    """
    Model representing a SourceReference in MammalBase
    """
    citation = models.CharField(
        max_length=450,
        help_text="Enter the Citation of the Source Reference"
    )
    master_reference = models.ForeignKey(
        'MasterReference',
        on_delete = models.SET_NULL,
        blank=True,
        null=True,
        )
    STATUS = (
        (1, 'Created - Not verified'),
        (2, 'Verified - Accepted'),
        (3, 'Verified - Rejected'),
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS,
        default=1,
        help_text='Status of the Std. Reference'
    )
    doi = models.CharField(
        max_length=100,
        validators=[validate_doi],
        help_text="Enter the DOI number that begins with 10 followed by a period",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['citation']

    def get_absolute_url(self):
        """
        Returns the url to access a particular reference instance.
        """
        return reverse('source-reference-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.citation}"

class ReferenceRelation(BaseModel):
    source_reference = models.ForeignKey(SourceReference, on_delete=models.CASCADE)
    master_reference = models.ForeignKey(MasterReference, on_delete=models.CASCADE)
    relation = models.ForeignKey(
        'RelationClass',
        on_delete = models.CASCADE,
        )

    class Meta:
        unique_together = ('source_reference', 'master_reference',)

    def get_absolute_url(self):
        """
        Returns the url to access a particular EntityRelation instance.
        """
        return reverse('reference-relation-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object
        """
        return (
                f"{self.source_reference.citation} "
                f"({self.master_reference.citation})")

class UnitConversion(BaseModel):
    """
    Model representing a Unit conversion between two Units)
    """
    from_unit = models.ForeignKey(MasterUnit, on_delete=models.CASCADE, related_name='from_unit')
    to_unit = models.ForeignKey(MasterUnit, on_delete=models.CASCADE, related_name='to_unit')
    coefficient = models.DecimalField(
                             max_digits = 19,
                             decimal_places = 10)

    class Meta:
        ordering = ['from_unit', 'to_unit']
        unique_together = ('from_unit', 'to_unit',)

    def get_absolute_url(self):
        """
        Returns the url to access a particular relation instance.
        """
        return reverse('unit_conversion-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return (
            f"One {self.from_unit.name} "
            f"equals {str(float(self.coefficient))} "
            f"{self.to_unit.name}s ")

class UnitRelation(BaseModel):
    source_unit = models.ForeignKey('SourceUnit', on_delete=models.CASCADE)
    master_unit = models.ForeignKey('MasterUnit', on_delete=models.CASCADE)
    remarks = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text="Enter remarks for the Unit Relation"
    )

    class Meta:
        unique_together = ('source_unit', 'master_unit',)

    def get_absolute_url(self):
        """
        Returns the url to access a particular UnitRelation instance.
        """
        return reverse('unit-relation-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object
        """
        return (
                f"{self.source_unit.name}: "
                f"{self.master_unit.name} "
                f"({self.master_unit.quantity_type})")

class TimePeriod(BaseModel):
    """
    Model representing a Time Period in MammalBase
    """

    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    name = models.CharField(max_length=50, help_text="Enter the Time Period")
    time_in_months = models.PositiveSmallIntegerField(
        default=12,
        help_text='Enter an estimate of Time Period in months.')

    class Meta:
        ordering = ['name']
        unique_together = ('reference','name')

    def get_absolute_url(self):
        """
        Returns the url to access a particular TimePeriod instance.
        """
        return reverse('time-unit-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.name}"

class DietSet(BaseModel):
    """
    Model representing a DietSet in MammalBase
    """

    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    taxon = models.ForeignKey(
        'SourceEntity',
        on_delete=models.CASCADE,
        limit_choices_to = (
                Q(entity__name='Genus') |
                Q(entity__name='Species') |
                Q(entity__name='Subspecies')),
        related_name='taxon_%(class)s',
        )
    location = models.ForeignKey(
        'SourceLocation',
        on_delete=models.CASCADE,
        blank=True,
        null = True,
        related_name='location_%(class)s',
        )
    gender = models.ForeignKey(
        'ChoiceValue',
        on_delete = models.SET_NULL,
        blank=True,
        null = True,
        limit_choices_to={'choice_set': 'Gender'},
        )
    sample_size = models.PositiveSmallIntegerField(
            default=0,
            help_text='Sample Size')
    cited_reference = models.CharField(
        blank=True,
        null=True,
        max_length=250,
        help_text=("Enter the original reference, if not this study. "
                   "If original, enter 'Original study'.")
        )
    time_period = models.ForeignKey(
        'TimePeriod',
        on_delete=models.CASCADE,
        blank=True,
        null = True,
        related_name='time_period_%(class)s',
        )
    method = models.ForeignKey(
        'SourceMethod',
        on_delete=models.CASCADE,
        blank=True,
        null = True,
        related_name='method_%(class)s',
        )
    study_time = models.CharField(
        blank=True,
        null=True,
        max_length=250,
        help_text="Enter the time when this study was performed.")
    data_quality_score = models.SmallIntegerField(
        blank=True,
        null=True,
        default=0,
        help_text="Data quality score for the data"
    )

    class Meta:
        ordering = ['taxon__name', 'reference']
#        unique_together = (
#                'reference',
#                'taxon',
#                'location',
#                'gender',
#                'sample_size',
#                'cited_reference',
#                'time_period',
#                'method')

    def get_absolute_url(self):
        """
        Returns the url to access a particular DietSet instance.
        """
        return reverse('diet-set-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.taxon} - {self.reference} "

    def calculate_data_quality_score(self):
        score = 0

        # 1. Taxon quality
        entity = self.taxon.entity.name
        if entity in ('Species', 'Subspecies'):
            score += 1

        # 2. The weight of having a reported citation of the data in the diet
        c_reference = self.cited_reference
        if c_reference == 'Original study':
            score += 2
        elif c_reference:
            score += 1

        # 3. The weight of source quality in the diet
        try:
            master = self.reference.master_reference.type
        except: # FIX: except what? ValueError?
            score += 0
        else:
            if master == 'journal-article':
                score += 3
            elif master == 'book':
                score += 2
            elif master == 'dataset':
                score += 1

        # 4. The weight of having a described method in the diet
        method = self.method
        if method:
            score += 2

        # 5. The weight of food item taxonomy
        diet_set_items = DietSetItem.objects.filter(
                diet_set=self,
                food_item__tsn__rank_id__gt=100)
        if diet_set_items.count():
            score += (2 * diet_set_items.count()) // diet_set_items.count()

        return score

class DietSetItem(BaseModel):
    """
    Model representing a DietSetItem in MammalBase
    """

    diet_set = models.ForeignKey(
        'DietSet',
        on_delete = models.CASCADE,
        )
    food_item = models.ForeignKey(
        'FoodItem',
        on_delete = models.CASCADE,
        )
    # Sortable, see. https://nemecek.be/blog/4/django-how-to-let-user-re-ordersort-table-of-content-with-drag-and-drop
    list_order = models.PositiveSmallIntegerField(
        default=100_000,
        help_text='List order on Diet Set'
    )
    percentage = models.DecimalField(default=0, decimal_places=3, max_digits=9)

    class Meta:
        unique_together = ('diet_set', 'food_item')
        ordering = ['list_order','-percentage']

    def clean(self):
        if self.percentage < 0:
            raise ValidationError(gettext_lazy(
                    'Only positive numbers are accepted.'))
#        if self.percentage > 100:
#            raise ValidationError(gettext_lazy(
#                    'Only numbers between 0 and 100 are accepted.'))

    def get_absolute_url(self):
        """
        Returns the url to access a particular DietSetItem instance.
        """
        return reverse('diet-set-item-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.diet_set} - {self.food_item}"

# https://resources.rescale.com/using-database-views-in-django-orm/
class ViewMasterTraitValue(models.Model):
    """
    Model representing a MasterTraitValue results as a MySQL view in MammalBase
    """
    id = models.BigIntegerField(primary_key=True)
    master_id = models.ForeignKey(
        'MasterEntity',
        to_field="id",
        db_column="master_id",
        on_delete=models.DO_NOTHING
    )
    master_entity_name = models.CharField(max_length=200)
    master_attribute_id = models.ForeignKey(
        'MasterAttribute',
        to_field="id",
        db_column="master_attribute_id",
        on_delete=models.DO_NOTHING
    )
    master_attribute_name = models.CharField(max_length=200)
    traits_references = models.CharField(max_length=400, blank=True, null=True)
    assigned_values = models.CharField(max_length=400, blank=True, null=True)
    n_distinct_value = models.PositiveSmallIntegerField()
    n_value = models.PositiveSmallIntegerField()
    n_supporting_value = models.PositiveSmallIntegerField()
    trait_values = models.CharField(max_length=400, blank=True, null=True)
    trait_selected = models.CharField(max_length=400, blank=True, null=True)
    trait_references = models.CharField(max_length=400, blank=True, null=True)
    value_percentage = models.DecimalField(
        blank = True,
        null=True,
        default=0,
        decimal_places=3,
        max_digits=7
    )

    class Meta:
        managed = False
        db_table = 'mb_view_master_trait_values'
        ordering = ['id','master_attribute_name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular Master Attribute instance.
        """
        return reverse(
                'master-attribute-detail',
                args=[str(self.master_attribute_id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return f"{self.master_attribute_name} - {self.trait_selected} "
