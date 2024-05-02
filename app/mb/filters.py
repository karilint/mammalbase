"""Django filters defined here
"""
import django_filters
from itis.models import TaxonomicUnits
from .models import (
    DietSet,
    MasterAttribute,
    MasterEntity,
    MasterReference,
    ProximateAnalysis,
    ProximateAnalysisItem,
    SourceAttribute,
    SourceEntity,
    SourceReference,
    TimePeriod,
    ViewMasterTraitValue,
    ViewProximateAnalysisTable,
    SourceLocation,
    MasterLocation)

from itis.models import TaxonomicUnits

class DietSetFilter(django_filters.FilterSet):
    taxon__name = django_filters.CharFilter(lookup_expr='icontains', label='Taxon contains')
    location__name = django_filters.CharFilter(lookup_expr='icontains', label='Location contains')
    time_period__name = django_filters.CharFilter(
        lookup_expr='icontains', label='Time period contains')
    method__name = django_filters.CharFilter(lookup_expr='icontains', label='Method contains')

    class Meta:
        model = DietSet
        fields = ['taxon__name', 'location__name', 'time_period__name', 'method__name']

class FoodItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Food Item contains')
    part__caption = django_filters.CharFilter(
        lookup_expr='icontains', label='Part contains')
    tsn__hierarchy_string = django_filters.CharFilter(
        lookup_expr='icontains', label='TSN hierarchy contains')
    tsn__hierarchy = django_filters.CharFilter(lookup_expr='icontains', label='TSN taxon contains')

    class Meta:
        model = DietSet
        fields = ['name', 'part__caption', 'tsn__hierarchy_string', 'tsn__hierarchy']

class MasterAttributeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains', label='Trait contains')
    reference__citation = django_filters.CharFilter(
        lookup_expr='icontains', label='Reference contains')

    class Meta:
        model = MasterAttribute
        fields = ['name', 'reference__citation',]

class MasterEntityFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains', label='Taxon contains')
    taxon__higher_classification = django_filters.CharFilter(
        lookup_expr='icontains', label='Higher Classification contains')

    class Meta:
        model = MasterEntity
        fields = ['name', 'taxon__higher_classification',]

class MasterReferenceFilter(django_filters.FilterSet):
    citation = django_filters.CharFilter(lookup_expr='icontains', label='Reference contains')

    class Meta:
        model = MasterReference
        fields = ['citation',]

class ProximateAnalysisFilter(django_filters.FilterSet):
    location__name = django_filters.CharFilter(lookup_expr='icontains', label='Study Area contains')
    method__name = django_filters.CharFilter(lookup_expr='icontains', label='Method contains')
    reference__citation = django_filters.CharFilter(
        lookup_expr='icontains', label='Reference contains')

    model = ProximateAnalysis
    class Meta:
        fields = ['reference__citation']

class ProximateAnalysisItemFilter(django_filters.FilterSet):
    forage__name = django_filters.CharFilter(
        lookup_expr='icontains', label='Forage contains')
    forage__part__caption = django_filters.CharFilter(
        lookup_expr='icontains', label='Part contains')
    location__name = django_filters.CharFilter(
        lookup_expr='icontains', label='Study Area contains')
    proximate_analysis__reference__citation = django_filters.CharFilter(
        lookup_expr='icontains', label='Reference contains')
    forage__tsn__hierarchy = django_filters.CharFilter(
        lookup_expr='icontains', label='TSN taxon contains')

    model = ProximateAnalysisItem
    class Meta:
        fields = ['forage',
                  'forage__part__caption',
                  'location',
                  'cited_reference',
                  'forage__tsn__hierarchy',
        ]

class SourceAttributeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Attribute contains')
    reference__citation = django_filters.CharFilter(
        lookup_expr='icontains', label='Reference contains')

    class Meta:
        model = SourceAttribute
        fields = ['name', 'reference__citation',]

class SourceEntityFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains', label='Taxon contains')
    reference__citation = django_filters.CharFilter(
        lookup_expr='icontains', label='Reference contains')

    class Meta:
        model = SourceEntity
        fields = ['name', 'reference__citation',]

class SourceReferenceFilter(django_filters.FilterSet):
    citation = django_filters.CharFilter(lookup_expr='icontains', label='Reference contains')

    class Meta:
        model = SourceReference
        fields = ['citation',]

class TaxonomicUnitsFilter(django_filters.FilterSet):
    tsn = django_filters.NumberFilter(label='Taxonomic Serial Number (TSN)')
    completename = django_filters.CharFilter(
        lookup_expr='icontains', label='Complete Name contains')
    hierarchy = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = TaxonomicUnits
        fields = ['tsn', 'completename', 'hierarchy', ]

class TimePeriodFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name contains')
    reference__citation = django_filters.CharFilter(
        lookup_expr='icontains', label='Reference contains')
    class Meta:
        model = TimePeriod
        fields = ['name', 'reference__citation', ]

class ViewMasterTraitValueFilter(django_filters.FilterSet):
    master_entity_name = django_filters.CharFilter(lookup_expr='icontains', label='Taxon contains')

    model = ViewMasterTraitValue
    class Meta:
        fields = ['id',
                  'master_id',
                  'master_entity_name',
                  'master_attribute_id',
                  'master_attribute_name',
                  'assigned_values',
                  'n_distinct_value',
                  'n_value',
                  'trait_values',
                  'trait_selected','value_percentage',
        ]

class ViewProximateAnalysisTableFilter(django_filters.FilterSet):
    tsn__hierarchy = django_filters.CharFilter(lookup_expr='icontains', label='Hierarchy contains')
    tsn__completename = django_filters.CharFilter(lookup_expr='icontains', label='Taxon contains')
    part = django_filters.CharFilter(lookup_expr='icontains', label='Part contains')

    model = ViewProximateAnalysisTable
    class Meta:
        fields = ['id',
                  'tsn',
                  'tsn__completename',
                  'tsn__hierarchy',
                  'tsn__hierarchystring',
                  'part',
                  'cp_std',
                  'ee_std',
                  'cf_std',
                  'ash_std',
                  'nfe_std',
                  'n_taxa',
                  'n_reference',
                  'n_analysis',
        ]
        fields = ['id', 'tsn','tsn__completename','tsn__hierarchy','tsn__hierarchystring','part','cp_std','ee_std','cf_std','ash_std','nfe_std','n_taxa','n_reference','n_analysis',]

class SourceLocationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Location contains')
    reference__citation = django_filters.CharFilter(lookup_expr='icontains', label='Reference contains')

    class Meta:
        model = SourceLocation
        fields = ['name', 'reference__citation',]

class MasterLocationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name contains')
    reference__citation = django_filters.CharFilter(lookup_expr='icontains', label='Reference contains')

    class Meta:
        model = MasterLocation
        fields = ['name', 'reference__citation',]



