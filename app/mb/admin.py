"""Django admin configuration"""

from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from tdwg.models import Taxon
from itis.models import TaxonomicUnits
from .models import (
    AttributeGroupRelation,
    AttributeRelation,
    ChoiceSetOptionRelation,
    ChoiceValue,
    DietSetItem,
    DietSet,
    EntityClass,
    EntityRelation,
    FoodItem,
    MasterAttribute,
    MasterAttributeGroup,
    MasterChoiceSetOption,
    MasterEntity,
    MasterReference,
    ProximateAnalysisItem,
    ProximateAnalysis,
    SourceAttribute,
    SourceChoiceSetOptionValue,
    SourceChoiceSetOption,
    SourceEntity,
    SourceLocation,
    SourceMeasurementValue,
    SourceMethod,
    SourceReference,
    SourceStatistic,
    SourceUnit,
    TimePeriod,
    MasterUnit,
    RelationClass,
    ReferenceRelation,
    UnitConversion,
    UnitRelation)

admin.site.register([Taxon, ])
admin.site.register([TaxonomicUnits, ])

# admin.site.register(
# [Name,
# Reference,
# Location,
# QualifierName,
# StratigraphicQualifier,
# Qualifier,
# StructuredName,
# Relation,])

# @admin.register(Name)
# class NameAdmin(admin.ModelAdmin):
#    list_display = ['name', ]
#    search_fields = ['name', ]
#    history_list_display = ['name', ]


@admin.register(AttributeGroupRelation)
class AttributeGroupRelationAdmin(SimpleHistoryAdmin):
    search_fields = ['group__name', 'attribute__name']
    list_filter = [('group', admin.RelatedOnlyFieldListFilter),
                   ('attribute', admin.RelatedOnlyFieldListFilter)]
    list_display = ('group_name', 'attribute_name')


    def group_name(self, obj):
        return obj.group.name

    def attribute_name(self, obj):
        return obj.attribute.name


@admin.register(AttributeRelation)
class AttributeRelationAdmin(SimpleHistoryAdmin):
    search_fields = [
        'source_attribute__name',
        'master_attribute__name',
        'master_attribute__reference__citation']
    list_filter = [('master_attribute', admin.RelatedOnlyFieldListFilter)]
    list_display = ('source_attribute_name',
                    'master_attribute_name', 'master_attribute_reference')

    def source_attribute_name(self, obj):
        return obj.source_attribute.name

    def master_attribute_name(self, obj):
        return obj.master_attribute.name

    def master_attribute_reference(self, obj):
        return obj.master_attribute.reference.citation


@admin.register(ChoiceSetOptionRelation)
class ChoiceSetOptionRelationAdmin(SimpleHistoryAdmin):
    search_fields = [
        'source_choiceset_option__name',
        'master_choiceset_option__name']
    list_filter = [
        ('master_choiceset_option',
         admin.RelatedOnlyFieldListFilter)]
    list_display = ('source_choiceset_option_name',
                    'master_choiceset_option_name')

    def source_choiceset_option_name(self, obj):
        return obj.source_choiceset_option.name

    def master_choiceset_option_name(self, obj):
        return obj.master_choiceset_option.name


@admin.register(ChoiceValue)
class ChoiceValueAdmin(SimpleHistoryAdmin):
    search_fields = ['choice_set', 'caption']
    list_filter = ['choice_set', 'caption']
    list_display = ('caption', 'choice_set')

    def choice_set(self, obj):
        return obj.choice_set.name

    def caption(self, obj):
        return obj.caption


@admin.register(DietSetItem)
class DietSetItemAdmin(SimpleHistoryAdmin):
    search_fields = ['diet_set__reference__citation', 'food_item__name']
    list_display = ('food_item_name', 'diet_set_reference')

    def diet_set_reference(self, obj):
        return obj.diet_set.reference.citation

    def food_item_name(self, obj):
        return obj.food_item.name


@admin.register(DietSet)
class DietSetAdmin(SimpleHistoryAdmin):
    search_fields = ['taxon__name', 'reference__citation']
    list_display = ('taxon_name', 'reference_citation')

    def taxon_name(self, obj):
        return obj.taxon.name

    def reference_citation(self, obj):
        return obj.reference.citation


@admin.register(EntityClass)
class EntityClassAdmin(SimpleHistoryAdmin):
    search_fields = ['name']
    list_filter = ['name']


@admin.register(EntityRelation)
class EntityRelationAdmin(SimpleHistoryAdmin):
    search_fields = [
        'source_entity__name',
        'master_entity__name',
        'master_entity__reference__citation']
    list_display = ('source_entity_name',
                    'master_entity_name', 'master_entity_reference')

    def source_entity_name(self, obj):
        return obj.source_entity.name

    def master_entity_name(self, obj):
        return obj.master_entity.name

    def master_entity_reference(self, obj):
        return obj.master_entity.reference.citation


@admin.register(FoodItem)
class FoodItemAdmin(SimpleHistoryAdmin):
    search_fields = ['name']
    list_filter = [('part', admin.RelatedOnlyFieldListFilter)]
    list_display = ('name', 'part')


@admin.register(MasterAttribute)
class MasterAttributeAdmin(SimpleHistoryAdmin):
    search_fields = ['entity__name', 'name', 'unit__print_name']
    list_filter = [('entity', admin.RelatedOnlyFieldListFilter),
                   'name', ('unit', admin.RelatedOnlyFieldListFilter)]
    list_display = ('name', 'entity_name', 'unit_print_name')

    def entity_name(self, obj):
        return obj.entity.name

    def unit_print_name(self, obj):
        return obj.unit.print_name


class MasterAttributeInline(admin.TabularInline):
    model = AttributeGroupRelation
    extra = 0


@admin.register(MasterAttributeGroup)
class MasterAttributeGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_master_attributes')
    inlines = [MasterAttributeInline]

    def get_master_attributes(self, obj):
        master_attributes = obj.masterattribute_set.all()
        attribute_names = ', '.join(attr.name for attr in master_attributes)
        return attribute_names

    get_master_attributes.short_description = 'Master Attributes'


@admin.register(MasterChoiceSetOption)
class MasterChoiceSetOptionAdmin(SimpleHistoryAdmin):
    search_fields = ['master_attribute__name', 'name']
    list_filter = [('master_attribute', admin.RelatedOnlyFieldListFilter)]
    list_display = ('name', 'master_attribute_name')

    def master_attribute_name(self, obj):
        return obj.master_attribute.name


@admin.register(MasterEntity)
class MasterEntityAdmin(SimpleHistoryAdmin):
    search_fields = ['name']
    list_filter = [('entity', admin.RelatedOnlyFieldListFilter)]
    list_display = ('name', 'entity')


@admin.register(MasterReference)
class MasterReferenceAdmin(SimpleHistoryAdmin):
    search_fields = ['citation']
    list_filter = ['type', 'year']
    list_display = ('citation', 'type', 'year')


@admin.register(ProximateAnalysisItem)
class ProximateAnalysisItemAdmin(SimpleHistoryAdmin):
    search_fields = ['proximate_analysis__reference__citation', 'forage__name']
    list_display = ('forage_name', 'proximate_analysis_reference')

    def proximate_analysis_reference(self, obj):
        return obj.proximate_analysis.reference.citation

    def forage_name(self, obj):
        return obj.forage.name


@admin.register(ProximateAnalysis)
class ProximateAnalysisAdmin(SimpleHistoryAdmin):
    search_fields = ['reference__citation']


@admin.register(SourceAttribute)
class SourceAttributeAdmin(SimpleHistoryAdmin):
    search_fields = ['entity__name', 'name']
    list_filter = [
        ('entity',
         admin.RelatedOnlyFieldListFilter),
        ('master_attribute',
         admin.RelatedOnlyFieldListFilter),
        'type']
    list_display = ('name', 'entity_name', 'type')

    def entity_name(self, obj):
        return obj.entity.name


@admin.register(SourceChoiceSetOptionValue)
class SourceChoiceSetOptionValueAdmin(SimpleHistoryAdmin):
    search_fields = [
        'source_choiceset_option__source_attribute__name',
        'source_choiceset_option__name']
    list_display = ('source_choiceset_option_source_attribute_name',
                    'source_choiceset_option_name')

    def source_choiceset_option_source_attribute_name(self, obj):
        return obj.source_choiceset_option.source_attribute.name

    def source_choiceset_option_name(self, obj):
        return obj.source_choiceset_option.name


@admin.register(SourceChoiceSetOption)
class SourceChoiceSetOptionAdmin(SimpleHistoryAdmin):
    search_fields = ['source_attribute__name', 'name']


@admin.register(SourceEntity)
class SourceEntityAdmin(SimpleHistoryAdmin):
    search_fields = ['name']
    list_display = ('name', 'entity')
    list_filter = [('entity', admin.RelatedOnlyFieldListFilter)]
    
    def entity(self, obj):
        return obj.entity.name

    
@admin.register(SourceLocation)
class SourceLocationAdmin(SimpleHistoryAdmin):
    search_fields = ['name']


@admin.register(SourceMeasurementValue)
class SourceMeasurementValueAdmin(SimpleHistoryAdmin):
    search_fields = ['source_attribute__name', 'n_total']


@admin.register(SourceMethod)
class SourceMethodAdmin(SimpleHistoryAdmin):
    search_fields = ['name']


@admin.register(SourceReference)
class SourceReferenceAdmin(SimpleHistoryAdmin):
    search_fields = ['citation']
    list_filter = ['status']
    list_display = ('citation', 'status')


@admin.register(SourceStatistic)
class SourceStatisticAdmin(SimpleHistoryAdmin):
    search_fields = ['name']


@admin.register(SourceUnit)
class SourceUnitAdmin(SimpleHistoryAdmin):
    search_fields = ['name']


@admin.register(TimePeriod)
class TimePeriodAdmin(SimpleHistoryAdmin):
    search_fields = ['name']
    list_filter = ['time_in_months']
    list_display = ('name', 'time_in_months')


admin.site.register(MasterUnit, SimpleHistoryAdmin)
admin.site.register(ReferenceRelation, SimpleHistoryAdmin)
admin.site.register(RelationClass, SimpleHistoryAdmin)
admin.site.register(UnitConversion, SimpleHistoryAdmin)
admin.site.register(UnitRelation, SimpleHistoryAdmin)
