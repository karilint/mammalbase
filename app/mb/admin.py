# pylint: disable=C0115,C0116
""" mb.admin

This module defines Django admin classes for the models in the mb app.

Each class specifies a set of fields to display in the admin interface,
as well as filters, search fields, autocomplete fields, and inline editing
to enhance usability and performance.

The SimpleHistoryAdmin class is used to display the history of changes to each model.

"""

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
    Event,
    FoodItem,
    MasterAttribute,
    MasterAttributeGroup,
    MasterChoiceSetOption,
    MasterEntity,
    MasterLocation,
    MasterReference,
    Occurrence,
    ProximateAnalysisItem,
    ProximateAnalysis,
    SourceAttribute,
    SourceChoiceSetOptionValue,
    SourceChoiceSetOption,
    SourceEntity,
    SourceHabitat,
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

class MyModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.created_by:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

class AttributeGroupRelationInline(admin.TabularInline):
    model = AttributeGroupRelation
    extra = 0


class AttributeRelationInline(admin.TabularInline):
    model = AttributeRelation
    extra = 0


@admin.register(AttributeGroupRelation)
class AttributeGroupRelationAdmin(SimpleHistoryAdmin):
    search_fields = ['group__name', 'attribute__name']
    list_filter = [('group', admin.RelatedOnlyFieldListFilter),
                   ('attribute', admin.RelatedOnlyFieldListFilter)]
    list_display = ('group', 'attribute_name')

    def attribute_name(self, obj):
        return obj.attribute.name

    attribute_name.admin_order_field = 'attribute__name'
    attribute_name.short_description = 'Attribute'


@admin.register(AttributeRelation)
class AttributeRelationAdmin(SimpleHistoryAdmin):
    search_fields = [
        'source_attribute__name',
        'master_attribute__name',
        'master_attribute__reference__citation']
    list_filter = [('master_attribute', admin.RelatedOnlyFieldListFilter)]
    list_display = ('source_attribute_name',
                    'master_attribute_name', 'master_attribute_reference')
    autocomplete_fields = ['source_attribute']

    def source_attribute_name(self, obj):
        return obj.source_attribute.name

    source_attribute_name.admin_order_field = 'source_attribute__name'
    source_attribute_name.short_description = 'Source Attribute'

    def master_attribute_name(self, obj):
        return obj.master_attribute.name

    master_attribute_name.admin_order_field = 'master_attribute__name'
    master_attribute_name.short_description = 'Master Attribute'

    def master_attribute_reference(self, obj):
        return obj.master_attribute.reference.citation

    master_attribute_reference.short_description = 'Master Attribute Reference'
    master_attribute_reference.admin_order_field = 'master_attribute__reference__citation'


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
    autocomplete_fields = ['source_choiceset_option']

    def source_choiceset_option_name(self, obj):
        return obj.source_choiceset_option.name

    source_choiceset_option_name.short_description = 'Source Choice Set Option'
    source_choiceset_option_name.admin_order_field = 'source_choiceset_option__name'

    def master_choiceset_option_name(self, obj):
        return obj.master_choiceset_option.name

    master_choiceset_option_name.short_description = 'Master Choice Set Option'
    master_choiceset_option_name.admin_order_field = 'master_choiceset_option__name'


@admin.register(ChoiceValue)
class ChoiceValueAdmin(SimpleHistoryAdmin):
    search_fields = ['choice_set', 'caption']
    list_filter = ['choice_set', 'caption']
    list_display = ('caption', 'choice_set')


@admin.register(DietSetItem)
class DietSetItemAdmin(SimpleHistoryAdmin):
    search_fields = ['diet_set__reference__citation', 'food_item__name']
    list_display = ('food_item_name', 'diet_set_reference')
    autocomplete_fields = ['diet_set', 'food_item']

    def food_item_name(self, obj):
        return obj.food_item.name

    food_item_name.short_description = 'Food Item'
    food_item_name.admin_order_field = 'food_item__name'

    def diet_set_reference(self, obj):
        return obj.diet_set.reference.citation

    diet_set_reference.short_description = 'Reference'
    diet_set_reference.admin_order_field = 'diet_set__reference__citation'


@admin.register(DietSet)
class DietSetAdmin(SimpleHistoryAdmin):
    search_fields = ['taxon__name', 'reference__citation']
    list_filter = ['data_quality_score', 'sample_size']
    list_display = ('taxon', 'reference_name')
    autocomplete_fields = ['taxon']

    def reference_name(self, obj):
        return obj.reference.citation

    reference_name.short_description = 'Reference'
    reference_name.admin_order_field = 'reference__citation'


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
    list_display = ('source_entity',
                    'master_entity', 'master_entity_reference')
    list_filter = [('relation_status', admin.RelatedOnlyFieldListFilter),
                   ('data_status', admin.RelatedOnlyFieldListFilter)]
    autocomplete_fields = ['source_entity', 'master_entity']

    def master_entity_reference(self, obj):
        return obj.master_entity.reference.citation

    master_entity_reference.short_description = 'Master Entity Reference'
    master_entity_reference.admin_order_field = 'master_entity__reference__citation'

@admin.register(Event)
class EventAdmin(SimpleHistoryAdmin):
    list_display = ('verbatim_event_date', 'source_habitat', )

@admin.register(FoodItem)
class FoodItemAdmin(SimpleHistoryAdmin):
    search_fields = ['name']
    list_filter = [('part', admin.RelatedOnlyFieldListFilter),
                   ('is_cultivar', admin.BooleanFieldListFilter)]
    list_display = ('food_item_name',)
    autocomplete_fields = ['tsn', 'pa_tsn']

    def food_item_name(self, obj):
        return obj.name

    food_item_name.admin_order_field = 'name'
    food_item_name.short_description = 'Food Item'

    def food_item_part(self, obj):
        return obj.part.caption

    food_item_part.admin_order_field = 'part__caption'


@admin.register(MasterAttribute)
class MasterAttributeAdmin(SimpleHistoryAdmin):
    search_fields = ['entity__name', 'name', 'unit__print_name']
    list_filter = [('entity', admin.RelatedOnlyFieldListFilter),
                   'name', ('unit', admin.RelatedOnlyFieldListFilter)]
    list_display = ('name', 'unit')
    inlines = [AttributeGroupRelationInline]


@admin.register(MasterAttributeGroup)
class MasterAttributeGroupAdmin(SimpleHistoryAdmin):
    search_fields = ['name', 'masterattribute__name']
    list_display = ('name', 'get_master_attributes')
    list_filter = [('masterattribute', admin.RelatedOnlyFieldListFilter)]
    inlines = [AttributeGroupRelationInline]

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
    list_display = ('name',)
    autocomplete_fields = ['taxon']

@admin.register(MasterLocation)
class MasterLocationAdmin(SimpleHistoryAdmin):
    search_fields = ['name']

@admin.register(MasterReference)
class MasterReferenceAdmin(SimpleHistoryAdmin):
    search_fields = ['citation']
    list_filter = ['type', 'year']
    list_display = ('citation',)


@admin.register(Occurrence)
class OccurrenceAdmin(SimpleHistoryAdmin):
    list_display = ('source_location', 'source_entity', )

@admin.register(ProximateAnalysisItem)
class ProximateAnalysisItemAdmin(SimpleHistoryAdmin):
    search_fields = ['proximate_analysis__reference__citation', 'forage__name']
    list_display = ('forage_name', 'proximate_analysis_reference')
    autocomplete_fields = ['forage']

    def forage_name(self, obj):
        return obj.forage.name

    forage_name.short_description = 'Forage'
    forage_name.admin_order_field = 'forage__name'

    def proximate_analysis_reference(self, obj):
        return obj.proximate_analysis.reference.citation

    proximate_analysis_reference.short_description = 'Reference'
    proximate_analysis_reference.admin_order_field = 'proximate_analysis__reference__citation'


@admin.register(ProximateAnalysis)
class ProximateAnalysisAdmin(SimpleHistoryAdmin):
    search_fields = ['reference__citation']
    list_display = ('reference_citation',)

    def reference_citation(self, obj):
        return obj.reference.citation

    reference_citation.short_description = 'Reference'
    reference_citation.admin_order_field = 'reference__citation'


@admin.register(SourceAttribute)
class SourceAttributeAdmin(SimpleHistoryAdmin):
    search_fields = ['entity__name', 'name']
    list_filter = [
        ('master_attribute',
         admin.RelatedOnlyFieldListFilter),
        'type']
    list_display = ('name', )
    inlines = [AttributeRelationInline]


@admin.register(SourceChoiceSetOptionValue)
class SourceChoiceSetOptionValueAdmin(SimpleHistoryAdmin):
    search_fields = [
        'source_choiceset_option__source_attribute__name',
        'source_choiceset_option__name']
    list_display = ('source_choiceset_option_source_attribute_name',
                    'source_choiceset_option_name')
    autocomplete_fields = ['source_entity', 'source_choiceset_option']

    def source_choiceset_option_source_attribute_name(self, obj):
        return obj.source_choiceset_option.source_attribute.name

    source_choiceset_option_source_attribute_name.short_description = 'Source Attribute'
    source_choiceset_option_source_attribute_name.admin_order_field = \
        'source_choiceset_option__source_attribute__name'

    def source_choiceset_option_name(self, obj):
        return obj.source_choiceset_option.name

    source_choiceset_option_name.short_description = 'Source Choice Set Option'
    source_choiceset_option_name.admin_order_field = 'source_choiceset_option__name'


@admin.register(SourceChoiceSetOption)
class SourceChoiceSetOptionAdmin(SimpleHistoryAdmin):
    search_fields = ['source_attribute__name', 'name']
    list_display = ('source_attribute_name', 'source_choice_set_option')
    autocomplete_fields = ['source_attribute']

    def source_attribute_name(self, obj):
        return obj.source_attribute.name

    source_attribute_name.short_description = 'Source Attribute'
    source_attribute_name.admin_order_field = 'source_attribute__name'

    def source_choice_set_option(self, obj):
        return obj.name

    source_choice_set_option.short_description = 'Source Choice Set Option'
    source_choice_set_option.admin_order_field = 'name'


@admin.register(SourceEntity)
class SourceEntityAdmin(SimpleHistoryAdmin):
    search_fields = ['name']
    list_display = ('name',)
    list_filter = [('entity', admin.RelatedOnlyFieldListFilter)]
    autocomplete_fields = ['taxon']


@admin.register(SourceHabitat)
class SourceHabitatAdmin(SimpleHistoryAdmin):
    search_fields = ['habitat_type']
    list_display = ('habitat_type',)
    list_filter = ['habitat_type']
    
@admin.register(SourceLocation)
class SourceLocationAdmin(SimpleHistoryAdmin):
    search_fields = ['name']
    list_display = ('name',)


@admin.register(SourceMeasurementValue)
class SourceMeasurementValueAdmin(SimpleHistoryAdmin):
    search_fields = ['source_attribute__name', 'n_total']
    list_display = ('source_attribute_name', 'n_total')
    autocomplete_fields = ['source_entity', 'source_attribute']

    def source_attribute_name(self, obj):
        return obj.source_attribute.name

    source_attribute_name.short_description = 'Source Attribute'
    source_attribute_name.admin_order_field = 'source_attribute__name'


@admin.register(SourceMethod)
class SourceMethodAdmin(SimpleHistoryAdmin):
    search_fields = ['name']
    list_display = ('name',)


@admin.register(SourceReference)
class SourceReferenceAdmin(SimpleHistoryAdmin):
    search_fields = ['citation']
    list_filter = ['status']
    list_display = ('citation',)


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
    list_display = ('name', )


@admin.register(TaxonomicUnits)
class TaxonomiUnitsAdmin(admin.ModelAdmin):
    search_fields = ['tsn', 'completename']
    list_display = ('tsn', 'completename')


@admin.register(Taxon)
class TaxonAdmin(admin.ModelAdmin):
    search_fields = ['scientific_name']
    list_display = ('scientific_name',)


admin.site.register(MasterUnit, SimpleHistoryAdmin)
admin.site.register(ReferenceRelation, SimpleHistoryAdmin)
admin.site.register(RelationClass, SimpleHistoryAdmin)
admin.site.register(UnitConversion, SimpleHistoryAdmin)
admin.site.register(UnitRelation, SimpleHistoryAdmin)
