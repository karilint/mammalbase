from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from tdwg.models import Taxon
from mb.models import models, location_models
from itis.models import TaxonomicUnits

admin.site.register([Taxon, ])
admin.site.register([TaxonomicUnits, ])

# admin.site.register([Name, Reference, Location, QualifierName, StratigraphicQualifier, Qualifier, StructuredName, Relation,])

# @admin.register(Name)
# class NameAdmin(admin.ModelAdmin):
#    list_display = ['name', ]
#    search_fields = ['name', ]
#    history_list_display = ['name', ]


@admin.register(models.AttributeGroupRelation)
class AttributeGroupRelationAdmin(SimpleHistoryAdmin):
    search_fields = ['group__name', 'attribute__name']
    list_filter = [('group', admin.RelatedOnlyFieldListFilter),
                   ('attribute', admin.RelatedOnlyFieldListFilter)]

@admin.register(models.AttributeRelation)
class AttributeRelationAdmin(SimpleHistoryAdmin):
    search_fields = [
        'source_attribute__name',
        'master_attribute__name',
        'master_attribute__reference__citation']
    list_filter = [('master_attribute', admin.RelatedOnlyFieldListFilter)]

@admin.register(models.ChoiceSetOptionRelation)
class ChoiceSetOptionRelationAdmin(SimpleHistoryAdmin):
    search_fields = [
        'source_choiceset_option__name',
        'master_choiceset_option__name']
    list_filter = [
        ('master_choiceset_option',
         admin.RelatedOnlyFieldListFilter)]

@admin.register(models.ChoiceValue)
class ChoiceValueAdmin(SimpleHistoryAdmin):
    search_fields = ['choice_set', 'caption']
    list_filter = ['choice_set', 'caption']

@admin.register(models.DietSetItem)
class DietSetItemAdmin(SimpleHistoryAdmin):
    search_fields = ['diet_set__reference__citation', 'food_item__name']

@admin.register(models.DietSet)
class DietSetAdmin(SimpleHistoryAdmin):
    search_fields = ['taxon__name', 'reference__citation']

@admin.register(models.EntityClass)
class EntityClassAdmin(SimpleHistoryAdmin):
    search_fields = ['name']
    list_filter = ['name']

@admin.register(models.EntityRelation)
class EntityRelationAdmin(SimpleHistoryAdmin):
    search_fields = [
        'source_entity__name',
        'master_entity__name',
        'master_entity__reference__citation']

@admin.register(models.FoodItem)
class FoodItemAdmin(SimpleHistoryAdmin):
    search_fields = ['name']
    list_filter = [('part', admin.RelatedOnlyFieldListFilter)]

@admin.register(models.MasterAttribute)
class MasterAttributeAdmin(SimpleHistoryAdmin):
    search_fields = ['entity__name', 'name', 'unit__print_name']
    list_filter = [('entity', admin.RelatedOnlyFieldListFilter),
                   'name', ('unit', admin.RelatedOnlyFieldListFilter)]

@admin.register(models.MasterAttributeGroup)
class MasterAttributeGroupAdmin(admin.ModelAdmin):
    pass

@admin.register(models.MasterChoiceSetOption)
class MasterChoiceSetOptionAdmin(SimpleHistoryAdmin):
    search_fields = ['master_attribute__name', 'name']
    list_filter = [('master_attribute', admin.RelatedOnlyFieldListFilter)]

@admin.register(models.MasterEntity)
class MasterEntityAdmin(SimpleHistoryAdmin):
    search_fields = ['name']
    list_filter = [('entity', admin.RelatedOnlyFieldListFilter)]

@admin.register(models.MasterReference)
class MasterReferenceAdmin(SimpleHistoryAdmin):
    search_fields = ['citation']
    list_filter = ['type', 'year']

@admin.register(models.ProximateAnalysisItem)
class ProximateAnalysisItemAdmin(SimpleHistoryAdmin):
    search_fields = ['proximate_analysis__reference__citation', 'forage__name']

@admin.register(models.ProximateAnalysis)
class ProximateAnalysisAdmin(SimpleHistoryAdmin):
    search_fields = ['reference__citation']

@admin.register(models.SourceAttribute)
class SourceAttributeAdmin(SimpleHistoryAdmin):
    search_fields = ['entity__name', 'name']
    list_filter = [
        ('entity',
         admin.RelatedOnlyFieldListFilter),
        ('master_attribute',
         admin.RelatedOnlyFieldListFilter),
        'type']

@admin.register(models.SourceChoiceSetOptionValue)
class SourceChoiceSetOptionValueAdmin(SimpleHistoryAdmin):
    search_fields = [
        'source_choiceset_option__source_attribute__name',
        'source_choiceset_option__name']

@admin.register(models.SourceChoiceSetOption)
class SourceChoiceSetOptionAdmin(SimpleHistoryAdmin):
    search_fields = ['source_attribute__name', 'name']

@admin.register(models.SourceEntity)
class SourceEntityAdmin(SimpleHistoryAdmin):
    search_fields = ['name']

@admin.register(location_models.SourceLocation)
class SourceLocationAdmin(SimpleHistoryAdmin):
    search_fields = ['name']

@admin.register(models.SourceMeasurementValue)
class SourceMeasurementValueAdmin(SimpleHistoryAdmin):
    search_fields = ['source_attribute__name', 'n_total']

@admin.register(models.SourceMethod)
class SourceMethodAdmin(SimpleHistoryAdmin):
    search_fields = ['name']

@admin.register(models.SourceReference)
class SourceReferenceAdmin(SimpleHistoryAdmin):
    search_fields = ['citation']
    list_filter = ['status']

@admin.register(models.SourceStatistic)
class SourceStatisticAdmin(SimpleHistoryAdmin):
    search_fields = ['name']

@admin.register(models.SourceUnit)
class SourceUnitAdmin(SimpleHistoryAdmin):
    search_fields = ['name']

@admin.register(models.TimePeriod)
class TimePeriodAdmin(SimpleHistoryAdmin):
    search_fields = ['name']
    list_filter = ['time_in_months']

admin.site.register(models.MasterUnit, SimpleHistoryAdmin)
admin.site.register(models.ReferenceRelation, SimpleHistoryAdmin)
admin.site.register(models.RelationClass, SimpleHistoryAdmin)
admin.site.register(models.UnitConversion, SimpleHistoryAdmin)
admin.site.register(models.UnitRelation, SimpleHistoryAdmin)