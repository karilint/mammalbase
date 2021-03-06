from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django_userforeignkey.models.fields import UserForeignKey
from django.core.validators import MaxValueValidator, MinValueValidator
from simple_history.models import HistoricalRecords
from itis.models import TaxonomicUnits

# For doi validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_doi(value):
    if not value.startswith( '10.' ):
        raise ValidationError(
            _('Value "%(value)s" does not begin with 10 followed by a period'),
            params={'value': value},
        )

class CustomQuerySet(QuerySet):
    def delete(self):
        self.update(is_active=False)

class ActiveManager(models.Manager):
    def is_active(self):
        return self.model.objects.filter(is_active=True)

    def get_queryset(self):
        return CustomQuerySet(self.model, using=self._db)

# https://medium.com/@KevinPavlish/add-common-fields-to-all-your-django-models-bce033ac2cdc
class BaseModel(models.Model):
    """
    A base model including basic fields for each Model
    see. https://pypi.org/project/django-userforeignkey/
    """
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = UserForeignKey(auto_user_add=True, verbose_name="The user that is automatically assigned", related_name='createdby_%(class)s')
    modified_by = UserForeignKey(auto_user=True, verbose_name="The user that is automatically assigned", related_name='modifiedby_%(class)s')
# https://django-simple-history.readthedocs.io/en/2.6.0/index.html
    history = HistoricalRecords(
        history_change_reason_field=models.TextField(null=True),
        inherit=True)
# https://stackoverflow.com/questions/5190313/django-booleanfield-how-to-set-the-default-value-to-true
    is_active = models.BooleanField(default=True, help_text='Is the record active')
    objects = ActiveManager()

# https://stackoverflow.com/questions/4825815/prevent-delete-in-django-model
    def delete(self):
        self.is_active = False
        self.save()

    class Meta:
        abstract = True


class AttributeRelation(BaseModel):
    source_attribute = models.ForeignKey('SourceAttribute', on_delete=models.CASCADE)
    master_attribute = models.ForeignKey('MasterAttribute', on_delete=models.CASCADE)
    remarks = models.TextField(blank=True, null=True, max_length=500, help_text="Enter remarks for the Attribute Relation")

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
        return '{0} ({1}) {2}'.format(self.source_attribute.name,self.master_attribute.name,self.master_attribute.reference)


class ChoiceValue(BaseModel):
    """
    Model representing a ChoiceValue in MammalBase
    """

    choice_set = models.CharField(max_length=25, help_text="Enter the Choice Set of the ChoiceValue")
    caption = models.CharField(max_length=25, help_text="Enter the Caption of the ChoiceValue")
#    link = models.URLField(max_length=200, help_text="Enter a valid URL for the Source Reference", blank=True, null=True,)

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
        return '%s - %s ' % (self.choice_set, self.caption)

class ChoiceSetOptionRelation(BaseModel):
    source_choiceset_option = models.ForeignKey('SourceChoiceSetOption', on_delete=models.CASCADE)
    master_choiceset_option = models.ForeignKey('MasterChoiceSetOption', on_delete=models.CASCADE)
    remarks = models.TextField(blank=True, null=True, max_length=500, help_text="Enter remarks for the ChoiceSetOption Relation")

    class Meta:
      unique_together = ('source_choiceset_option', 'master_choiceset_option',)

    def get_absolute_url(self):
        """
        Returns the url to access a particular ChoiceSetOptionRelation instance.
        """
        return reverse('choiceset_option-relation-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object
        """
        return '{0} - {1}'.format(self.source_choiceset_option.name,self.master_choiceset_option.name)


class EntityClass(BaseModel):
    """
    Model representing a Entity Class in MammalBase
    """

    name = models.CharField(max_length=50, help_text="Enter the Name of the Entity Class")
#    link = models.URLField(max_length=200, help_text="Enter a valid URL for the Source Reference", blank=True, null=True,)

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular Entity Class instance.
        """
        return reverse('entity-class-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s' % (self.name)


class RelationClass(BaseModel):
    """
    Model representing a RelationClass in MammalBase
    """

    name = models.CharField(max_length=25, help_text="Enter the Name of the RelationClass")

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular RelationClass instance.
        """
        return reverse('relation-class-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s' % (self.name)


class FoodItem(BaseModel):
    """
    Model representing a FoodItem in MammalBase
    """
    name = models.CharField(max_length=250, unique=True, help_text="Enter the Name of the FoodItem")
    part = models.ForeignKey(
        'ChoiceValue',
        on_delete = models.SET_NULL,
        null = True,
        limit_choices_to={'choice_set': 'FoodItemPart'},
        )
    tsn = models.ForeignKey(TaxonomicUnits, to_field="tsn", db_column="tsn", blank=True, null=True, on_delete = models.SET_NULL, related_name='tsn_food')
    pa_tsn = models.ForeignKey(TaxonomicUnits, to_field="tsn", db_column="pa_tsn", blank=True, null=True, on_delete = models.SET_NULL, related_name='tsn_pa')

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
                while(i>=0):
                    part=self.part.caption
                    if part=='CARRION':
                        part='WHOLE'
                    pa=ViewProximateAnalysisTable.objects.filter(tsn__hierarchy_string__endswith=tsn_hierarchy[i]).filter(part__exact=part)
                    if len(pa)==1:
                        self.pa_tsn=pa.all()[0].tsn
                        break
                    i=i-1
            super().save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s' % (self.name)


class MasterAttribute(BaseModel):
    """
    Model representing a MasterAttribute in MammalBase
    """
    reference = models.ForeignKey(
        'MasterReference',
        on_delete = models.CASCADE,
        )
    entity = models.ForeignKey(
        'EntityClass',
        on_delete = models.CASCADE,
        )
    name = models.CharField(max_length=250, help_text="Enter the Name of the Master Attribute")
    unit = models.ForeignKey(
    'MasterUnit',blank=True, null=True,
    on_delete = models.CASCADE,
    )
    remarks = models.TextField(blank=True, null=True, max_length=500, help_text="Enter remarks for the Master Attribute")

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
            return '%s: %s (%s)' % (self.entity.name, self.name, self.unit.print_name)
        else:
            return '%s: %s' % (self.entity.name, self.name)

class MasterChoiceSetOption(BaseModel):
    """
    Model representing a MasterChoiceSetOption in MammalBase
    """
    master_attribute = models.ForeignKey(
        'MasterAttribute',
        on_delete = models.CASCADE,
        )
    display_order = models.PositiveSmallIntegerField(default=10, help_text='Display order on choises')
    name = models.CharField(max_length=250, help_text="Enter the Name of the Master Attribute")
    description = models.TextField(blank=True, null=True, max_length=1500, help_text="Enter description for the Master Choice Set Option")

    class Meta:
        ordering = ['master_attribute__name','display_order']

    def get_absolute_url(self):
        """
        Returns the url to access a particular MasterChoiceSetOption instance.
        """
        return reverse('master-choiceset-option', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s - %s ' % (self.master_attribute.name, self.name)


class MasterEntity(BaseModel):
    """
    Model representing a MasterEntity in MammalBase
    """
    reference = models.ForeignKey(
        'MasterReference',
        on_delete = models.CASCADE,
        )
    entity = models.ForeignKey(
        'EntityClass',
        on_delete = models.CASCADE,
        )
    name = models.CharField(max_length=250, help_text="Enter the Name of the Master Entity")

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
        return '%s' % (self.name)

class MasterLocation(BaseModel):
    """
    Model representing a MasterLocation in MammalBase
    """
    reference = models.ForeignKey(
        'MasterReference',
        on_delete = models.CASCADE,
        )
    name = models.CharField(max_length=250, help_text="Enter the Name of the Master Location")
    tgn = models.PositiveSmallIntegerField(default=0, blank=True, null=True, help_text='Enter Thesaurus of Geographic Names id')

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


class MasterReference(BaseModel):
    """
    Model representing a Standard Reference in MammalBase
    """

    type = models.CharField(max_length=25, help_text="Enter the Type of the Standard Reference", blank=True, null=True,)
#    doi = models.URLField(max_length=200, help_text="Enter a valid DOI URL for the Standard Reference", blank=True, null=True,)
    doi = models.CharField(max_length=100, validators=[validate_doi], help_text="Enter the DOI number that begins with 10 followed by a period", blank=True, null=True,)
    uri = models.URLField(max_length=200, help_text="Enter the Uniform Resource Identifier link", blank=True, null=True,)
    first_author = models.CharField(max_length=50, help_text="Enter the name of the first author of the Standard Reference", blank=True, null=True,)
    year = models.IntegerField(validators=[MinValueValidator(1800), MaxValueValidator(2100)], blank=True, null=True,)
    title = models.CharField(max_length=400, help_text="Enter the Title of the Standard Reference", blank=True, null=True,)
    container_title = models.CharField(max_length=100, help_text="Enter the Container Title of the Standard Reference", blank=True, null=True,)
    volume = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4000)], blank=True, null=True,)
    issue = models.CharField(max_length=5, help_text="Enter the Issue of the Standard Reference", blank=True, null=True,)
    page = models.CharField(max_length=50, help_text="Enter the Page(s) of the Standard Reference", blank=True, null=True,)
    citation = models.CharField(max_length=400, help_text="Enter the Citation of the Standard Reference")
#    link = models.URLField(max_length=200, help_text="Enter a valid URL for the Source Reference", blank=True, null=True,)

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
        return '%s' % (self.citation)

class MasterUnit(BaseModel):
    """
    Model representing a MasterUnit in MammalBase
    """
    name = models.CharField(max_length=25, help_text="Enter the name of the Master Unit")
    print_name = models.CharField(max_length=25, help_text="Enter the Print value of the name of a Master Unit")
    quantity_type = models.CharField(max_length=25, help_text="Enter the Quantity type of the Master Unit")
    unit_value = models.DecimalField(
                         max_digits = 19,
                         decimal_places = 10)
    remarks = models.TextField(blank=True, null=True, max_length=500, help_text="Enter remarks for the Master Unit")

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
        return '%s: %s (%s)' % (self.quantity_type, self.name, self.print_name)

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
    name = models.CharField(max_length=250, help_text="Enter the Name of the Attribute")
    TYPE = (
        (0, 'Not Specified'),
        (1, 'Numerical variable'),
        (2, 'Categorical variable'),
    )
    type = models.PositiveSmallIntegerField(choices=TYPE, default=3, help_text='Select the type of the Attribute')
    remarks = models.TextField(blank=True, null=True, max_length=500, help_text="Enter remarks for the Attribute")

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
        return '%s - %s ' % (self.entity.name, self.name)


class SourceChoiceSetOption(BaseModel):
    """
    Model representing a SourceChoiceSetOption in MammalBase
    """
    source_attribute = models.ForeignKey(
        'SourceAttribute',
        on_delete = models.CASCADE,
        )
    display_order = models.PositiveSmallIntegerField(default=10, help_text='Display order on choises')
    name = models.CharField(max_length=250, help_text="Enter the Source Choice Set Option")
    description = models.TextField(blank=True, null=True, max_length=500, help_text="Enter the description for the Source Choice Set Option")

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
        return '%s - %s ' % (self.source_attribute.name, self.name)

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
        return '%s - %s ' % (self.source_choiceset_option.source_attribute.name, self.source_choiceset_option.name)

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
    name = models.CharField(max_length=250, help_text="Enter the Name of the Source Entity")

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
        return '%s' % (self.name)

class SourceLocation(BaseModel):
    """
    Model representing a SourceLocation in MammalBase
    """
    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    name = models.CharField(max_length=250, help_text="Enter the Name of the Source Location")

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
    n_total = models.PositiveSmallIntegerField(default=0, blank=True, null=True, help_text='n for total number of specimens measured.')
    n_unknown = models.PositiveSmallIntegerField(default=0, blank=True, null=True, help_text='n for total number of unknown gender specimens measured.')
    n_male = models.PositiveSmallIntegerField(default=0, blank=True, null=True, help_text='n for total number of male specimens measured.')
    n_female = models.PositiveSmallIntegerField(default=0, blank=True, null=True, help_text='n for total number of female specimens measured.')
    minimum = models.DecimalField(max_digits=19, decimal_places=10, help_text='Minimum measurement value reported.')
    maximum = models.DecimalField(max_digits=19, decimal_places=10, help_text='Maximum measurement value reported.')
    mean = models.DecimalField(max_digits=19, decimal_places=10, help_text='Mean of measurement values reported.')
    std = models.DecimalField(max_digits=19, decimal_places=10, default=None, blank=True, null=True, help_text='Standard deviation of measurement values reported.')
    source_unit = models.ForeignKey(
        'SourceUnit',
        null=True, blank=True,
        on_delete = models.SET_NULL,
        )
    unit = models.CharField(
        null=True,
        blank=True,
        max_length=250, help_text='Measurement unit reported.')
    def clean(self):
        # Don't allow wrong n values.
        if self.n_total != self.n_unknown + self.n_male + self.n_female:
            raise ValidationError(_('n total needs to be sum of all n fields.'))
        if self.minimum > self.maximum:
            raise ValidationError(_('Measurement error: min > max.'))
        if self.mean < self.minimum or self.mean > self.maximum :
            raise ValidationError(_('Measurement error: mean outside min or max.'))
        if self.n_total == 0 or self.n_total == 1:
            self.std = None
        if self.std != None and self.std > self.maximum - self.minimum:
            raise ValidationError(_('Measurement error: std is too large.'))

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
        return '%s: %s ' % (self.source_attribute.name, str(self.n_total))

class SourceMethod(BaseModel):
    """
    Model representing a Source Method in MammalBase
    """

    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    name = models.CharField(max_length=500, help_text="Enter the method described in the Reference")

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
        return '%s' % (self.name)

class SourceUnit(BaseModel):
    """
    Model representing a SourceUnit in MammalBase
    """
    name = models.CharField(max_length=25, help_text="Enter the name of the Source Unit")
    remarks = models.TextField(blank=True, null=True, max_length=500, help_text="Enter remarks for the Source Unit")

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
        return '%s' % (self.name)

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
    remarks = models.TextField(blank=True, null=True, max_length=500, help_text="Enter remarks for the Entity Relation")

    class Meta:
      unique_together = ('source_entity', 'master_entity','relation')

# What is this?
    def level_1(self):
        return self.name_one.qualifier.level

    def get_absolute_url(self):
        """
        Returns the url to access a particular EntityRelation instance.
        """
        return reverse('entity-relation-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object
        """
        return '{0} ({1}) {2}'.format(self.source_entity.name,self.master_entity.name,self.master_entity.reference)

class SourceReference(BaseModel):
    """
    Model representing a SourceReference in MammalBase
    """
    citation = models.CharField(max_length=450, help_text="Enter the Citation of the Source Reference")
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
    status = models.PositiveSmallIntegerField(choices=STATUS, default=1, help_text='Status of the Std. Reference')
    doi = models.CharField(max_length=100, validators=[validate_doi], help_text="Enter the DOI number that begins with 10 followed by a period", blank=True, null=True,)

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
        return '%s' % (self.citation)

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
        return '{0} ({1})'.format(self.source_reference.citation,self.master_reference.citation)

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
        return 'One %s equals %s %ss ' % (self.from_unit.name, str(float(self.coefficient)), self.to_unit.name)

class UnitRelation(BaseModel):
    source_unit = models.ForeignKey('SourceUnit', on_delete=models.CASCADE)
    master_unit = models.ForeignKey('MasterUnit', on_delete=models.CASCADE)
    remarks = models.TextField(blank=True, null=True, max_length=500, help_text="Enter remarks for the Unit Relation")

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
        return '{0}: {1} ({2})'.format(self.source_unit.name,self.master_unit.name,self.master_unit.quantity_type)

class TimePeriod(BaseModel):
    """
    Model representing a Time Period in MammalBase
    """

    reference = models.ForeignKey(
        'SourceReference',
        on_delete = models.CASCADE,
        )
    name = models.CharField(max_length=50, help_text="Enter the Time Period")
    time_in_months = models.PositiveSmallIntegerField(default=12, help_text='Enter an estimate of Time Period in months.')

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
        return '%s' % (self.name)

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
        limit_choices_to=Q(entity__name='Genus') | Q(entity__name='Species') | Q(entity__name='Subspecies'),
		related_name='taxon_%(class)s',
		)
    location = models.ForeignKey(
		'SourceLocation',
		on_delete=models.CASCADE,
        null = True,
		related_name='location_%(class)s',
		)
    gender = models.ForeignKey(
        'ChoiceValue',
        on_delete = models.SET_NULL,
        null = True,
        limit_choices_to={'choice_set': 'Gender'},
        )
    sample_size = models.PositiveSmallIntegerField(default=0, help_text='Sample Size')
    cited_reference = models.CharField(null=True, max_length=250, help_text="Enter the original reference, if not this study.")
    time_period = models.ForeignKey(
		'TimePeriod',
		on_delete=models.CASCADE,
        null = True,
		related_name='time_period_%(class)s',
		)
    method = models.ForeignKey(
		'SourceMethod',
		on_delete=models.CASCADE,
        null = True,
		related_name='method_%(class)s',
		)
    study_time = models.CharField(null=True, max_length=250, help_text="Enter the time when this study was performed.")

    class Meta:
        ordering = ['taxon__name', 'reference']
#        unique_together = ('reference','taxon','location', 'gender', 'sample_size', 'cited_reference', 'time_period', 'method')

    def get_absolute_url(self):
        """
        Returns the url to access a particular DietSet instance.
        """
        return reverse('diet-set-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s - %s ' % (self.taxon, self.reference)


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
    list_order = models.PositiveSmallIntegerField(default=0, help_text='List order on Diet Set')
    percentage = models.DecimalField(default=0, decimal_places=2, max_digits=6,
              validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        unique_together = ('diet_set', 'food_item')
        ordering = ['list_order','-percentage']

    def clean(self):
        if self.percentage < 0:
            raise ValidationError(_('Only numbers between 0 and 100 are accepted.'))
        if self.percentage > 100:
            raise ValidationError(_('Only numbers between 0 and 100 are accepted.'))

    def get_absolute_url(self):
        """
        Returns the url to access a particular DietSetItem instance.
        """
        return reverse('diet-set-item-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s - %s ' % (self.diet_set, self.food_item)

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
    cited_reference = models.CharField(blank=True, null=True, max_length=250, help_text="Enter the original reference, if not this study.")
    method = models.ForeignKey(
		'SourceMethod',
		on_delete=models.CASCADE,
        null = True,
		)
    study_time = models.CharField(blank=True, null=True, max_length=250, help_text="Enter the time when this study was performed.")

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
        return '%s' % (self.reference)

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
    cited_reference = models.CharField(blank = True, null=True, max_length=250, help_text="Enter the original reference, if not this study.")
    sample_size = models.PositiveSmallIntegerField(blank = True, null=True, default=0, help_text='Sample size')
    dm_reported = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7,
              validators=[MinValueValidator(0), MaxValueValidator(1000)])
    moisture_reported = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7,
              validators=[MinValueValidator(0), MaxValueValidator(1000)])
    cp_reported = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7,
              validators=[MinValueValidator(0), MaxValueValidator(1000)])
    ee_reported = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7,
              validators=[MinValueValidator(0), MaxValueValidator(1000)])
    cf_reported = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7,
              validators=[MinValueValidator(0), MaxValueValidator(1000)])
    ash_reported = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7,
              validators=[MinValueValidator(0), MaxValueValidator(1000)])
    nfe_reported = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7,
              validators=[MinValueValidator(0), MaxValueValidator(1000)])
    total_carbohydrates_reported = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7,
              validators=[MinValueValidator(0), MaxValueValidator(1000)])
    cp_std = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7,
              validators=[MinValueValidator(0), MaxValueValidator(100)])
    ee_std = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7,
              validators=[MinValueValidator(0), MaxValueValidator(100)])
    cf_std = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7,
              validators=[MinValueValidator(0), MaxValueValidator(100)])
    ash_std = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7,
              validators=[MinValueValidator(0), MaxValueValidator(100)])
    nfe_std = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7,
              validators=[MinValueValidator(0), MaxValueValidator(100)])
    transformation = models.CharField(blank = True, null=True, max_length=250,)
    remarks = models.CharField(blank = True, null=True, max_length=250, help_text="Enter remarks.")

    class Meta:
        ordering = ['proximate_analysis','forage']

    def clean(self):
        if self.dm_reported < 0:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.dm_reported > 1000:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.moisture_reported < 0:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.moisture_reported > 1000:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.cp_reported < 0:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.cp_reported > 1000:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.ee_reported < 0:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.ee_reported > 1000:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.cf_reported < 0:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.cf_reported > 1000:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.ash_reported < 0:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.ash_reported > 1000:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.nfe_reported < 0:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.nfe_reported > 1000:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.total_carbohydrates_reported < 0:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))
        if self.total_carbohydrates_reported > 1000:
            raise ValidationError(_('Only numbers between 0 and 1000 are accepted.'))

    def get_absolute_url(self):
        """
        Returns the url to access a particular ProximateAnalysisItem instance.
        """
        return reverse('proximate-analysis-item-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s - %s ' % (self.proximate_analysis, self.forage)

# https://resources.rescale.com/using-database-views-in-django-orm/
class ViewMasterTraitValue(models.Model):
    """
    Model representing a MasterTraitValue results as a MySQL view in MammalBase
    """
    id = models.BigIntegerField(primary_key=True)
    master_id = models.ForeignKey('MasterEntity', to_field="id", db_column="master_id", on_delete=models.DO_NOTHING)
    master_entity_name = models.CharField(max_length=200)
    master_attribute_id = models.ForeignKey('MasterAttribute', to_field="id", db_column="master_attribute_id", on_delete=models.DO_NOTHING)
    master_attribute_name = models.CharField(max_length=200)
    traits_references = models.CharField(max_length=400, blank=True, null=True)
    assigned_values = models.CharField(max_length=400, blank=True, null=True)
    n_distinct_value = models.PositiveSmallIntegerField()
    n_value = models.PositiveSmallIntegerField()
    n_supporting_value = models.PositiveSmallIntegerField()
    trait_values = models.CharField(max_length=400, blank=True, null=True)
    trait_selected = models.CharField(max_length=400, blank=True, null=True)
    trait_references = models.CharField(max_length=400, blank=True, null=True)
    value_percentage = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7)

    class Meta:
        managed = False
        db_table = 'mb_table_master_trait_values'
        ordering = ['id','master_attribute_name']

    def get_absolute_url(self):
        """
        Returns the url to access a particular Master Attribute instance.
        """
        return reverse('master-attribute-detail', args=[str(self.master_attribute_id)])

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return '%s - %s ' % (self.master_attribute_name, self.trait_selected)

# https://resources.rescale.com/using-database-views-in-django-orm/
class ViewProximateAnalysisTable(models.Model):
    """
    Model representing a ProximateAnalysis results as a MySQL view in MammalBase
    """
    id = models.BigIntegerField(primary_key=True)
    tsn = models.ForeignKey(TaxonomicUnits, to_field="tsn", db_column="tsn", on_delete=models.DO_NOTHING)
    part = models.CharField(max_length=200)
    cp_std = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7)
    ee_std = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7)
    cf_std = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7)
    ash_std = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7)
    nfe_std = models.DecimalField(blank = True, null=True, default=0, decimal_places=3, max_digits=7)
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
        return '%s' % (self.tsn)
