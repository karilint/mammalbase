from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from tdwg.models import Taxon
from mb.models import models
from itis.models import TaxonomicUnits

admin.site.register([Taxon,])
admin.site.register([TaxonomicUnits,])

# admin.site.register([Name, Reference, Location, QualifierName, StratigraphicQualifier, Qualifier, StructuredName, Relation,])

#@admin.register(Name)
#class NameAdmin(admin.ModelAdmin):
#    list_display = ['name', ]
#    search_fields = ['name', ]
#    history_list_display = ['name', ]

@admin.register(models.MasterAttributeGroup)
class MasterAttributeGroupAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.AttributeGroupRelation, SimpleHistoryAdmin)
admin.site.register(models.AttributeRelation, SimpleHistoryAdmin)
admin.site.register(models.ChoiceValue, SimpleHistoryAdmin)
admin.site.register(models.ChoiceSetOptionRelation, SimpleHistoryAdmin)
admin.site.register(models.DietSet, SimpleHistoryAdmin)
admin.site.register(models.DietSetItem, SimpleHistoryAdmin)
admin.site.register(models.EntityClass, SimpleHistoryAdmin)
admin.site.register(models.EntityRelation, SimpleHistoryAdmin)
admin.site.register(models.FoodItem, SimpleHistoryAdmin)
admin.site.register(models.MasterAttribute, SimpleHistoryAdmin)
#admin.site.register(models.MasterAttributeGroup, SimpleHistoryAdmin)
admin.site.register(models.MasterChoiceSetOption, SimpleHistoryAdmin)
admin.site.register(models.MasterEntity, SimpleHistoryAdmin)
admin.site.register(models.MasterReference, SimpleHistoryAdmin)
admin.site.register(models.MasterUnit, SimpleHistoryAdmin)
admin.site.register(models.ProximateAnalysis, SimpleHistoryAdmin)
admin.site.register(models.ProximateAnalysisItem, SimpleHistoryAdmin)
admin.site.register(models.ReferenceRelation, SimpleHistoryAdmin)
admin.site.register(models.RelationClass, SimpleHistoryAdmin)
admin.site.register(models.SourceAttribute, SimpleHistoryAdmin)
admin.site.register(models.SourceChoiceSetOption, SimpleHistoryAdmin)
admin.site.register(models.SourceChoiceSetOptionValue, SimpleHistoryAdmin)
admin.site.register(models.SourceEntity, SimpleHistoryAdmin)
admin.site.register(models.SourceLocation, SimpleHistoryAdmin)
admin.site.register(models.SourceMeasurementValue, SimpleHistoryAdmin)
admin.site.register(models.SourceMethod, SimpleHistoryAdmin)
admin.site.register(models.SourceReference, SimpleHistoryAdmin)
admin.site.register(models.SourceStatistic, SimpleHistoryAdmin)
admin.site.register(models.SourceUnit, SimpleHistoryAdmin)
admin.site.register(models.TimePeriod, SimpleHistoryAdmin)
admin.site.register(models.UnitConversion, SimpleHistoryAdmin)
admin.site.register(models.UnitRelation, SimpleHistoryAdmin)
