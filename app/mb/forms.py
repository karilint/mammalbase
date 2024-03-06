from django import forms
from django_select2.forms import ModelSelect2Widget

from itis.models import TaxonomicUnits
from .models import (
    AttributeRelation,
    ChoiceSetOptionRelation,
    DietSet,
    DietSetItem,
    EntityRelation,
    FoodItem,
    MasterAttribute,
    MasterChoiceSetOption,
    MasterEntity,
    MasterReference,
    ProximateAnalysis,
    ProximateAnalysisItem,
    SourceAttribute,
    SourceChoiceSetOption,
    SourceChoiceSetOptionValue,
    SourceEntity,
    SourceMeasurementValue,
    SourceReference,
    TimePeriod)

class ReferenceWidget(ModelSelect2Widget):
    search_fields = ['title__icontains', 'first_author__icontains',]

class AttributeRelationForm(forms.ModelForm):
    class Meta:
        model = AttributeRelation
        fields = ('master_attribute', )

class ChoiceSetOptionRelationForm(forms.ModelForm):
    class Meta:
        model = ChoiceSetOptionRelation
        fields = ('master_choiceset_option', )

class TimePeriodWidget(ModelSelect2Widget):
    search_fields = ['name__icontains',]

class DietSetForm(forms.ModelForm):
    class Meta:
        model = DietSet
        fields = ('taxon', 'location', 'time_period', 'gender', 'sample_size', 'method', 'study_time', 'cited_reference', 'reference')
        widgets = {'time_period': TimePeriodWidget, }

    # https://stackoverflow.com/questions/28901089/use-field-value-in-limit-choices-to-in-django
    def __init__(self, *args, **kwargs):
        super(DietSetForm, self).__init__(*args, **kwargs)
        if self.instance.reference:
            self.fields['time_period'].queryset = TimePeriod.objects.filter(
                                                reference=self.instance.reference)

class FoodItemWidget(ModelSelect2Widget):
    search_fields = ['name__icontains',]

class DietSetItemForm(forms.ModelForm):
    class Meta:
        model = DietSetItem
        fields = ('percentage','food_item')
        widgets = {'food_item': FoodItemWidget, }

class EntityRelationForm(forms.ModelForm):
    class Meta:
        model = EntityRelation
        fields = ('source_entity', 'master_entity', 'relation', 'relation_status', 'data_status', )

class TSNWidget(ModelSelect2Widget):
    search_fields = ['completename__icontains', 'hierarchy__icontains','hierarchy_string__icontains',]

class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ('name', 'part', 'tsn' )
        widgets = {'tsn': TSNWidget, }

class MasterAttributeForm(forms.ModelForm):
    class Meta:
        model = MasterAttribute
        fields = ('name', 'unit', 'description', 'reference',)
        widgets = {'reference': ReferenceWidget, }

class MasterAttributeChoicesetOptionForm(forms.ModelForm):
    class Meta:
        model = MasterChoiceSetOption
        fields = ('name', 'display_order', 'description',)

class MasterChoiceSetOptionForm(forms.ModelForm):
    class Meta:
        model = MasterChoiceSetOption
        fields = ('master_attribute', 'name', 'display_order', 'description',)

class MasterEntityForm(forms.ModelForm):
    class Meta:
        model = MasterEntity
        fields = ('name', 'entity', 'reference',)
        widgets = {'reference': ReferenceWidget, }

class MasterReferenceForm(forms.ModelForm):
    class Meta:
        model = MasterReference
        fields = ('type', 'first_author', 'year', 'title', 'container_title', 'volume', 'issue', 'page', 'citation', 'doi', 'uri',)

# Sortable, see. https://nemecek.be/blog/4/django-how-to-let-user-re-ordersort-table-of-content-with-drag-and-drop
class OrderingForm(forms.Form):
    ordering = forms.CharField()

class SourceAttributeChoicesetOptionForm(forms.ModelForm):
    class Meta:
        model = SourceChoiceSetOption
        fields = ('name', 'display_order', 'description',)

class SourceAttributeForm(forms.ModelForm):
    class Meta:
        model = SourceAttribute
        fields = ('name', 'remarks', 'reference',)
        widgets = {'reference': ReferenceWidget, }

class SourceChoiceSetOptionForm(forms.ModelForm):
    class Meta:
        model = SourceChoiceSetOption
        fields = ('source_attribute', 'name', 'display_order', 'description',)

class OptionWidget(ModelSelect2Widget):
#    model = SourceChoiceSetOption
#    print(request.HttpRequest)
    search_fields = ['name__icontains',]
#    id = 496
#    queryset = SourceChoiceSetOption.objects.filter(source_attribute__id=id)
#    queryset = SourceChoiceSetOption.objects.filter(source_attribute__id=496)
#    queryset = SourceChoiceSetOption.objects.is_active()
#    def filter_queryset(self, request, term, field_id, queryset, **kwargs):
#    def filter_queryset(self):
#        queryset = self.queryset
#        return super().filter_queryset(request, term, field_id, self.queryset, **kwargs)
#    def filter_queryset(self, request, term, queryset, **dependent_fields):
#    def filter_queryset(self, request, term, queryset, **dependent_fields):
#        kwargs = super(ModelSelect2Mixin, self).kwargs
#        print('Hello')
#        print(super())
#        print(request.GET['se'])
#        print(request.GET.get('se'))
#        print(request)
#        print(dependent_fields['se'])
#        print(request.kwargs.GET['se'])
#       request.GET['id'] or request.POST['id']
#        print(request.parser_context['kwargs']['pk'])
#        queryset = SourceChoiceSetOption.objects.filter(source_attribute__id=496)
#        return queryset
##            return super().filter_queryset(request, term, queryset, **kwargs).filter(
#                source_attribute__id=496
#            )

#        queryset = SourceChoiceSetOption.objects.filter(source_attribute__id=496)
#            return super().filter_queryset(self, request, **kwargs)
#        return super().filter_queryset(self, request, term, queryset, **dependent_fields)
#        return super().filter_queryset(request, term, queryset=queryset, **dependent_fields)
class ProximateAnalysisForm(forms.ModelForm):
    class Meta:
        model = ProximateAnalysis
        fields = ('reference', 'method', 'location', 'study_time', 'cited_reference',)
        widgets = {'reference': ReferenceWidget, }

class ProximateAnalysisItemForm(forms.ModelForm):
    class Meta:
        model = ProximateAnalysisItem
        fields = ('forage', 'location', 'sample_size', 'measurement_determined_by', 'remarks'
            , 'moisture_reported', 'moisture_dispersion', 'moisture_measurement_method'
            , 'dm_reported', 'dm_dispersion', 'dm_measurement_method'
            , 'cp_reported', 'cp_dispersion', 'cp_measurement_method'
            , 'cf_reported', 'cf_dispersion', 'cf_measurement_method'
            , 'ash_reported', 'ash_dispersion', 'ash_measurement_method'
            , 'ee_reported', 'ee_dispersion', 'ee_measurement_method'
            , 'nfe_reported', 'nfe_dispersion', 'nfe_measurement_method', 'total_carbohydrates_reported', 'cited_reference')

class SourceChoiceSetOptionValueForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        sac = kwargs.pop('sac', None)
#        sac = kwargs.get('sac')
        print(sac)
        super(SourceChoiceSetOptionValueForm, self).__init__( *args, **kwargs)
# https://stackoverflow.com/questions/39785703/how-to-pass-variable-as-argument-in-meta-class-in-django-form
        source_choiceset_option = self.fields['source_choiceset_option']
        source_choiceset_option.queryset = SourceChoiceSetOption.objects.filter(
            source_attribute__id=sac
        )

    class Meta:
        model = SourceChoiceSetOptionValue
        fields = ('source_choiceset_option',)
        widgets = {'source_choiceset_option': OptionWidget(attrs={
                'data-minimum-input-length': 0, 'data-allow-clear': 'false',
                'data-placeholder': ("Choose Value"),
                'data-width': '75%',
            },)
         }

class SourceEntityForm(forms.ModelForm):
    class Meta:
        model = SourceEntity
        fields = ('name', 'entity', 'reference',)
        widgets = {'reference': ReferenceWidget, }

class MSW3TaxaWidget(ModelSelect2Widget):
    queryset = MasterEntity.objects.filter(reference_id=4)
    search_fields = ['name__icontains',]

class MatchStatusWidget(ModelSelect2Widget):
    queryset = MasterChoiceSetOption.objects.filter(master_attribute__name__contains='Match Type')
    search_fields = ['name__icontains',]

class SourceEntityRelationForm(forms.ModelForm):
    class Meta:
        model = EntityRelation
        fields = ('master_entity', 'relation_status', 'remarks', )
        widgets = {'master_entity': MSW3TaxaWidget, 'relation_status': MatchStatusWidget, }

class SourceEntityForm(forms.ModelForm):
    class Meta:
        model = SourceEntity
        fields = ('name', 'entity', 'reference',)
        widgets = {'reference': ReferenceWidget, }

class SourceMeasurementValueForm(forms.ModelForm):
    class Meta:
        model = SourceMeasurementValue
        fields = ('source_location'
            , 'gender'
            , 'n_total'
            , 'n_unknown'
            , 'n_female'
            , 'n_male'
            , 'minimum'
            , 'mean'
            , 'maximum'
            , 'std'
            , 'cited_reference'
            , 'source_unit', )

class SourceReferenceAttributeForm(forms.ModelForm):
    class Meta:
        model = SourceAttribute
        fields = ('name', 'remarks',)


class SourceReferenceForm(forms.ModelForm):
    class Meta:
        model = SourceReference
        fields = ('citation', 'status', 'doi', 'master_reference',)
        widgets = {'master_reference': ReferenceWidget, }

class TaxonomicUnitsForm(forms.ModelForm):
    class Meta:
        model = TaxonomicUnits
        fields = ('completename', 'tsn', 'kingdom_id', 'rank_id' )

    kingdom_id = forms.IntegerField(
        initial=0
        ,widget=forms.HiddenInput()
    )
    rank_id = forms.IntegerField(
        initial=0
        ,widget=forms.HiddenInput()
    )
        #widgets = {'kingdom_id': forms.HiddenInput()}

class TimePeriodForm(forms.ModelForm):
    class Meta:
        model = TimePeriod
        fields = ('name', 'time_in_months', 'reference', )
        widgets = {'reference': ReferenceWidget, }
