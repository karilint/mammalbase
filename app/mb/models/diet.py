""" mb.models.diet - 

This module should not be imported anywhere else than __init__.py!

To import models elsewhere use subpackage:
from mb.models import ModelName
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy

from app.itis.models import TaxonomicUnits
from app.mb.models.proximate_analysis import ViewProximateAnalysisTable
from .base_model import BaseModel

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
    # Sortable, see:
    # https://nemecek.be/blog/4/django-how-to-let-user-re-ordersort-table-of-content-with-drag-and-drop
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
        return f"{self.diet_set}-{self.food_item}"
    

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
        return f"{self.taxon}-{self.reference} "

    def calculate_data_quality_score(self):
        """
        Returns the data quality score. 
        Score is composed of the taxon quality, citation, how good the source is,
        desctiption and the precision of the food item
        """
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
        """
        Saves what is given to it
        """
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
    