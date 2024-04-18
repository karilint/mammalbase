import datetime, json
from decimal import * # TODO: fix star imports!
from django.core.exceptions import PermissionDenied
from django.db import connection, transaction
from django.db.models import Count, Max, F
from django.contrib.auth.decorators import (
    login_required, permission_required)
from django.contrib.auth.mixins import (
    PermissionRequiredMixin, UserPassesTestMixin)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.http import require_GET, require_POST
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.db import models
from django.db.models import Q

import requests
from requests_cache import CachedSession

from plotly import express as plotly_express
from plotly.offline import plot as plotly_offline_plot
from pandas import DataFrame as PandasDataFrame

from config.settings import ITIS_CACHE
from imports.tools import (
    create_return_data,
    create_tsn,
    generate_standard_values_pa)
from itis.models import TaxonomicUnits
from mb.filters import (
    DietSetFilter,
    FoodItemFilter,
    MasterAttributeFilter,
    MasterEntityFilter,
    MasterReferenceFilter,
    ProximateAnalysisFilter,
    ProximateAnalysisItemFilter,
    SourceAttributeFilter,
    SourceEntityFilter,
    SourceReferenceFilter,
    TaxonomicUnitsFilter,
    TimePeriodFilter,
    ViewProximateAnalysisTableFilter,
    MasterLocationFilter
    )
from mb.forms import (
    AttributeRelationForm,
    ChoiceSetOptionRelationForm,
    DietSetForm,
    DietSetItemForm,
    EntityRelationForm,
    FoodItemForm,
    MasterEntityForm,
    MasterAttributeForm,
    MasterAttributeChoicesetOptionForm,
    MasterChoiceSetOptionForm,
    MasterReferenceForm,
    OrderingForm,
    ProximateAnalysisForm,
    ProximateAnalysisItemForm,
    SourceAttributeForm,
    SourceAttributeChoicesetOptionForm,
    SourceChoiceSetOptionForm,
    SourceChoiceSetOptionValueForm,
    SourceEntityForm,
    SourceEntityRelationForm,
    SourceMeasurementValueForm,
    SourceReferenceAttributeForm,
    SourceReferenceForm,
    TaxonomicUnitsForm,
    TimePeriodForm)
from mb.models import (
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
    RelationClass,
    SourceAttribute,
    SourceChoiceSetOption,
    SourceChoiceSetOptionValue,
    SourceEntity,
    SourceMeasurementValue,
    SourceReference,
    TimePeriod,
    ViewMasterTraitValue,
    ViewProximateAnalysisTable,
    Occurrence,
    ChoiceValue,
    Event,
    SourceHabitat,
    MasterHabitat)
from mb.models.location_models import MasterLocation, LocationRelation, SourceLocation


# Error Pages
# https://blog.khophi.co/get-django-custom-error-views-right-first-time/
def server_error(request):
    return render(request, 'errors/500.html')

def not_found(request):
    return render(request, 'errors/404.html')

def permission_denied(request):
    return render(request, 'errors/403.html')

def bad_request(request):
    return render(request, 'errors/400.html')

def about_history(request):
    return render(request, 'mb/history.html',)

def index_about(request):
    return render(request, 'mb/index_about.html',)

def privacy_policy(request):
    return render(request, 'mb/privacy_policy.html',)

#@ratelimit(key='ip', rate='2/m')
def index(request):
    return render(request, 'mb/index.html',)

def index_diet(request):
    num_diet_taxa=DietSet.objects.is_active().values('taxon_id').distinct().count()
    num_diet_set=DietSet.objects.is_active().count()
    num_diet_set_item=DietSetItem.objects.is_active().count()
    num_food_item=DietSetItem.objects.is_active().values('food_item_id').distinct().count()
    latest=DietSet.objects.is_active().filter(reference__master_reference__is_active=True).order_by('-pk')[:10]
    return render(request, 'mb/index_diet.html', context={'num_diet_taxa':num_diet_taxa, 'num_diet_set':num_diet_set, 'num_diet_set_item':num_diet_set_item, 'num_food_item':num_food_item, 'latest':latest},)

def index_mammals(request):
    measurements=SourceReference.objects.is_active().filter(sourceattribute__type = 1).filter(status = 2).distinct().order_by('-pk')[:10]
    return render(request, 'mb/index_mammals.html', context={'measurements':measurements},)

def index_news(request):
    return render(request, 'mb/index_news.html',)

def index_proximate_analysis(request):
    num_PA_item=ProximateAnalysisItem.objects.is_active().values('forage_id').distinct().count()
    return render(request, 'mb/index_proximate_analysis.html', context={'num_PA_item':num_PA_item},)

def index_master_location_list(request):

    def string_contains(str1, str2):
        if str1.lower() in str2.lower():
            return True
        return False
    
    def remove_none_values(list):
        new_list = []
        for item in list:
            if item == None:
                continue
            new_list.append(item)
        return new_list

    def filter(objects, params):
        print("params: " + str(params))
        
        try:
            master_location = params["master_location"]
            for i in range(len(objects)):
                if master_location == "":
                    break
                if string_contains(master_location, objects[i].name) == False:
                    objects[i] = None
        except:
            pass
        
        """
        for object in objects:
            try:
                reference = params["reference"]
            except:
                break
            if reference == "":
                break
            if object.reference not in reference:
                objects.remove(object)
		"""
        """
        for object in objects:
            if params["master_habitat"] == "":
                break
            if object.master_habitat != params["master_habitat"]:
                objects.pop(object)
		"""
        objects = remove_none_values(objects)
        for object in objects:
            print("name: " + str(object.name))
            continue
        
        return objects

    params_set = False

    params = request.GET.dict()

    class MasterLocationView(models.Model):
        name = models.CharField(max_length=500) 
        reference = models.CharField(max_length=500) 
        master_habitats = models.TextField()
    
    def get_master_habitats(ml : MasterLocation):
        # Get MasterHabitats by MasterLocation
        mr = ml.reference

        try:
            master_habitats = MasterHabitat.objects.filter(reference=mr)
        except:
            return "nan"
        
        habitats = ""

        for master_habitat in master_habitats:
            habitats = habitats + f"{master_habitat.name} "

        

        return str(habitats)
    
    master_locations = MasterLocation.objects.filter()

    mls_with_habitat = []

    for x in master_locations:
        ml_view_obj = MasterLocationView()
        ml_view_obj.name = x.name
        ml_view_obj.reference = x.reference
        ml_view_obj.master_habitat = get_master_habitats(x)
        mls_with_habitat.append(ml_view_obj)
    
    mls_with_habitat = filter(mls_with_habitat, params)
    
    paginator = Paginator(mls_with_habitat, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return render(
        request,
        'mb/master_location_list.html',
        {'page_obj': page_obj, 'filter': filter,}
    )

def master_location_detail(request, pk):
    master_location = get_object_or_404(MasterLocation, id=pk)
    related_objects = MasterLocation.objects.filter(pk=master_location.higherGeographyID.id)
    occurrences = get_occurrences_by_masterlocation(master_location)
    return render(request, 'mb/master_location_detail.html', context={"master_location" : master_location, "related_objects" : related_objects, "occurrences" : occurrences},)

# Sortable, see. https://nemecek.be/blog/4/django-how-to-let-user-re-ordersort-table-of-content-with-drag-and-drop
@require_POST
def save_new_ordering(request):
    form = OrderingForm(request.POST)
    pk=0

    if form.is_valid():
        ordered_ids = form.cleaned_data["ordering"].split(',')
        n = len(ordered_ids)
        with transaction.atomic():
            i = 1
            for lookup_id in ordered_ids:
#                weight = 2*(n+1-i)/(n*(n+1))*100 Jernvall Calculation
                dsi = DietSetItem.objects.get(pk=lookup_id)
                diet_set = dsi.diet_set
                dsi.list_order = i
                dsi.save()
                i += 1
                pk=diet_set.pk
        return redirect('diet_set-detail', pk=pk)
    else:
        return redirect('diet_set-list')

def user_is_data_admin_or_contributor(user, data=None):
    if user.groups.filter(name='data_admin').exists():
        return True

    if user.groups.filter(name='data_contributor').exists():
        return True

    return False

def user_is_data_admin_or_owner(user, data):
    if user.groups.filter(name='data_admin').exists():
        return True

    if user.groups.filter(name='data_contributor').exists() and data.created_by == user:
        return True

    return False

class attribute_relation_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = AttributeRelation
    def get_success_url(self):
        attribute_relation = super(attribute_relation_delete, self).get_object()
        sa_id = attribute_relation.source_attribute.id
        return reverse_lazy(
            'source_attribute-detail',
            args=(sa_id,)
        )

def attribute_relation_detail(request, pk):
    attribute_relation = get_object_or_404(AttributeRelation, pk=pk, is_active=1)
    return render(request, 'mb/attribute_relation_detail.html', {'attribute_relation': attribute_relation})

@login_required
@permission_required('mb.edit_attribute_relation', raise_exception=True)
def attribute_relation_edit(request, pk):
    attribute_relation = get_object_or_404(AttributeRelation, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, attribute_relation):
        raise PermissionDenied

    if request.method == "POST":
        form = AttributeRelationForm(request.POST, instance=attribute_relation)
        if form.is_valid():
            attribute_relation = form.save(commit=False)
            attribute_relation.save()
            return redirect('mb/attribute_relation-detail', pk=attribute_relation.pk)
    else:
        form = AttributeRelationForm(instance=attribute_relation)
    return render(request, 'mb/attribute_relation_edit.html', {'form': form})

@login_required
@permission_required('mb.add_attribute_relation', raise_exception=True)
def attribute_relation_new(request, sa):
    source_attribute = get_object_or_404(SourceAttribute, pk=sa, is_active=1)
    if request.method == "POST":
        form = AttributeRelationForm(request.POST)
        if form.is_valid():
            attribute_relation = form.save(commit=False)
            attribute_relation.source_attribute = source_attribute
            attribute_relation.save()
            return redirect('source_attribute-detail', pk=attribute_relation.source_attribute.id)
    else:
        form = AttributeRelationForm()
    return render(request, 'mb/attribute_relation_edit.html', {'form': form})

class choiceset_option_relation_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = ChoiceSetOptionRelation
    def get_success_url(self):
        choiceset_option_relation = super(choiceset_option_relation_delete, self).get_object()
        sco_id = choiceset_option_relation.source_choiceset_option.id
        return reverse_lazy(
            'source_choiceset_option-detail',
            args=(sco_id,)
        )

def choiceset_option_relation_detail(request, pk):
    choiceset_option_relation = get_object_or_404(ChoiceSetOptionRelation, pk=pk, is_active=1)
    return render(request, 'mb/choiceset_option_relation_detail.html', {'choiceset_option_relation': choiceset_option_relation})

@login_required
@permission_required('mb.edit_choiceset_option_relation', raise_exception=True)
def choiceset_option_relation_edit(request, pk):
    choiceset_option_relation = get_object_or_404(ChoiceSetOptionRelation, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, choiceset_option_relation):
        raise PermissionDenied

    if request.method == "POST":
        form = ChoiceSetOptionRelationForm(request.POST, instance=choiceset_option_relation)
        if form.is_valid():
            choiceset_option_relation = form.save(commit=False)
            choiceset_option_relation.save()
            return redirect('mb/choiceset_option_relation-detail', pk=choiceset_option_relation.pk)
    else:
        form = ChoiceSetOptionRelationForm(instance=choiceset_option_relation)
    return render(request, 'mb/choiceset_option_relation_edit.html', {'form': form})

@login_required
@permission_required('mb.choiceset_option_relation', raise_exception=True)
def choiceset_option_relation_new(request, cso):
    choiceset_option = get_object_or_404(SourceChoiceSetOption, pk=cso, is_active=1)
    if request.method == "POST":
        form = ChoiceSetOptionRelationForm(request.POST)
        if form.is_valid():
            choiceset_option_relation = form.save(commit=False)
            choiceset_option_relation.source_choiceset_option = choiceset_option
            choiceset_option_relation.save()
            return redirect('source_choiceset_option-detail', pk=choiceset_option_relation.source_choiceset_option.id)
    else:
        form = ChoiceSetOptionRelationForm()
    return render(request, 'mb/choiceset_option_relation_edit.html', {'form': form})

@login_required
def data_check_detail(request):
    dsi = DietSetItem.objects.is_active().values('diet_set_id').order_by('diet_set_id').annotate(count=(Count('list_order')), max=(Max('list_order'))).exclude(count=F("max"))

    # Food item: missing part, TSN
    ds_data = DietSet.objects.raw("""
        select ds.id, count(dsi.id) n_dsi
        from mb_dietset ds
        left join mb_sourceentity se on se.id=ds.taxon_id
        left join mb_entityrelation er on er.source_entity_id=se.id and er.relation_id=1
        left join mb_masterentity me on me.id=er.master_entity_id and me.reference_id=4
        left join mb_dietsetitem dsi on dsi.diet_set_id=ds.id and dsi.is_active=1
        left join mb_fooditem fi on fi.id=dsi.food_item_id and fi.is_active=1
        left join itis_taxonomicunits tu on tu.tsn=fi.tsn
        left join mb_choicevalue part on part.id=fi.part_id and part.is_active=1
        where (fi.id is null or part.id is null or me.id is null) and ds.is_active=1
        group by ds.id
        order by count(dsi.id)
        """)

    return render(request, 'mb/data_check_detail.html', {'dsi': dsi, 'ds_data': ds_data, })

def diet_set_detail(request, pk):
	ds = get_object_or_404(DietSet, pk=pk, is_active=1)
	return render(request, 'mb/diet_set_detail.html', {'ds': ds})

class diet_set_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = DietSet
    success_url = reverse_lazy('diet_set-list')

    #https://stackoverflow.com/questions/53145279/edit-record-before-delete-django-deleteview
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.dietsetitem_set.all().delete()
        return super(diet_set_delete, self).delete(*args, **kwargs)

@login_required
@permission_required('mb.edit_diet_set', raise_exception=True)
def diet_set_edit(request, pk):
    diet_set = get_object_or_404(DietSet, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, diet_set):
        raise PermissionDenied

    if request.method == "POST":
        form = DietSetForm(request.POST, instance=diet_set)
        if form.is_valid():
            diet_set = form.save(commit=False)
            diet_set.save()
            return redirect('diet_set-detail', pk=diet_set.pk)
    else:
        form = DietSetForm(instance=diet_set)
    return render(request, 'mb/diet_set_edit.html', {'form': form})

def diet_set_list(request):
    f = DietSetFilter(request.GET, queryset=DietSet.objects.is_active().select_related())

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/diet_set_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

def diet_set_item_detail(request, pk):
    diet_set_item = get_object_or_404(DietSetItem, pk=pk, is_active=1)

    if diet_set_item.food_item.tsn is None:
        tsn_id = -1
        hierarchy = ''
        hierarchy_string = ''
        common_names = ''
    elif diet_set_item.food_item.tsn.tsn == 1:
        tsn_id = 1
        hierarchy = 'MINERAL'
        hierarchy_string = 'MINERAL'
        common_names = 'MINERAL'
    else:
        tsn_id = diet_set_item.food_item.tsn.tsn
        taxonomic_unit = get_object_or_404(TaxonomicUnits, tsn=tsn_id)

        response1 = requests.get("https://www.itis.gov/ITISWebService/jsonservice/getCommonNamesFromTSN?tsn="+str(tsn_id))
        r1 = response1.json()
        response3 = requests.get("https://www.itis.gov/ITISWebService/jsonservice/getFullHierarchyFromTSN?tsn="+str(tsn_id))
        r3 = response3.json()

        strings1 = []
        strings3 = []
        strings4 = []

        i=0
        while r3['hierarchyList']:
            strings1.append(r3['hierarchyList'][i]['tsn'])
            strings3.append(r3['hierarchyList'][i]['taxonName'])
            if r3['hierarchyList'][i]['tsn'] == str(tsn_id):
                break
            i += 1

        if str(r1['commonNames'][0]) != 'None':
            j=0
            while j < len(r1['commonNames']):
                strings4.append(r1['commonNames'][j]['commonName'])
                j += 1
            common_names = ', '.join(strings4)
        else:
            common_names = ''

        hierarchy_string = '-'.join(strings1)
        hierarchy = '-'.join(strings3)
#if request.POST['amount'] is not None:

        if len(hierarchy_string) > 0:
            taxonomic_unit.hierarchy_string = hierarchy_string
        else:
            taxonomic_unit.hierarchy_string = ''
        if len(hierarchy) > 0:
            taxonomic_unit.hierarchy = hierarchy
        else:
            taxonomic_unit.hierarchy = ''
        if len(common_names) > 0:
            taxonomic_unit.common_names = common_names
        else:
            taxonomic_unit.common_names = ''
        taxonomic_unit.tsn_update_date = datetime.datetime.now()
        taxonomic_unit.save()
    return render(request, 'mb/diet_set_item_detail.html', {'dsi': diet_set_item, 'common_names': common_names, 'hierarchy': hierarchy, 'hierarchy_string': hierarchy_string,}, )

class diet_set_item_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = DietSetItem
    def get_success_url(self):
        diet_set_item = super(diet_set_item_delete, self).get_object()
        ds_id = diet_set_item.diet_set.id
        return reverse_lazy(
            'diet_set-detail',
            args=(ds_id,)
        )

@login_required
@permission_required('mb.edit_diet_set_item', raise_exception=True)
def diet_set_item_edit(request, pk):
    diet_set_item = get_object_or_404(DietSetItem, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, diet_set_item):
        raise PermissionDenied

    if request.method == "POST":
        form = DietSetItemForm(request.POST, instance=diet_set_item)
        if form.is_valid():
            diet_set_item = form.save(commit=False)
            diet_set_item.save()
            return redirect('diet_set_item-detail', pk=diet_set_item.pk)
    else:
        form = DietSetItemForm(instance=diet_set_item)
    return render(request, 'mb/diet_set_item_edit.html', {'form': form})

@login_required
@permission_required('mb.add_diet_set_item', raise_exception=True)
def diet_set_item_new(request, diet_set):
    diet_set = get_object_or_404(DietSet, pk=diet_set, is_active=1)
    if request.method == "POST":
        form = DietSetItemForm(request.POST)
        if form.is_valid():
            diet_set_item = form.save(commit=False)
            diet_set_item.diet_set = diet_set
            diet_set_item.list_order = DietSetItem.objects.is_active().filter(diet_set_id=diet_set.id).count()+1
            diet_set_item.save()
            return redirect('diet_set-detail', pk=diet_set_item.diet_set.id)
    else:
        form = DietSetItemForm()
    return render(request, 'mb/diet_set_item_edit.html', {'form': form})

def diet_set_reference_list(request):
    f = MasterReferenceFilter(request.GET, queryset=MasterReference.objects
        .is_active()
        .filter(sourcereference__dietset__gte=0)
        .distinct())

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/diet_set_reference_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

# https://ultimatedjango.com/learn-django/lessons/delete-contact-full-lesson/
class entity_relation_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = EntityRelation
    def get_success_url(self):
        entity_relation = super(entity_relation_delete, self).get_object()
        se_id = entity_relation.source_entity.id
        return reverse_lazy(
            'source_entity-detail',
            args=(se_id,)
        )

def entity_relation_detail(request, pk):
    entity_relation = get_object_or_404(EntityRelation, pk=pk, is_active=1)
    return render(request, 'mb/entity_relation_detail.html', {'entity_relation': entity_relation})

@login_required
@permission_required('mb.edit_entity_relation', raise_exception=True)
def entity_relation_edit(request, pk):
    entity_relation = get_object_or_404(EntityRelation, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, entity_relation):
        raise PermissionDenied

    if request.method == "POST":
        form = EntityRelationForm(request.POST, instance=entity_relation)
        if form.is_valid():
            entity_relation = form.save(commit=False)
            entity_relation.save()
            return redirect('entity_relation-detail', pk=entity_relation.pk)
    else:
        form = EntityRelationForm(instance=entity_relation)
    return render(request, 'mb/entity_relation_edit.html', {'form': form})

class food_item_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = FoodItem
    success_url = reverse_lazy('food_item-list')

def food_item_detail(request, pk):
    food_item = get_object_or_404(FoodItem, pk=pk, is_active=1)
    sl = None
    if food_item.tsn is not None:
        sl = SynonymLinks.objects.filter(tsn=food_item.tsn)
        if len(sl) == 0:
            sl = None
        else:
            sl = sl[0]
        if food_item.tsn.hierarchy_string:
            tsn_hierarchy = food_item.tsn.hierarchy_string.split("-")
        else:
            tsn_hierarchy = ''
    else:
        tsn_hierarchy = ''

    i=len(tsn_hierarchy)-1
    pa = ViewProximateAnalysisTable.objects.none()

    while(i>=0):
        part=food_item.part.caption
        if part=='CARRION':
            part='WHOLE'
        pa=ViewProximateAnalysisTable.objects.filter(tsn__hierarchy_string__endswith=tsn_hierarchy[i]).filter(part__exact=part)
        if len(pa)==1:
            break
        i=i-1

    if pa.exists():
        proximate_analysis=pa.all()[0]
    else:
        proximate_analysis=pa.none()
    
    

    return render(request, 'mb/food_item_detail.html', {'proximate_analysis': proximate_analysis, 'food_item': food_item, 'synonym_link': sl})

@login_required
@permission_required('mb.edit_food_item', raise_exception=True)
def food_item_edit(request, pk):
    food_item = get_object_or_404(FoodItem, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, food_item):
        raise PermissionDenied

    if request.method == "POST":
        form = FoodItemForm(request.POST, instance=food_item)
        if form.is_valid():
            food_item = form.save(commit=False)
            food_item.save()
            return redirect('food_item-detail', pk=food_item.pk)
    else:
        form = FoodItemForm(instance=food_item)
    return render(request, 'mb/food_item_edit.html', {'form': form})

def food_item_list(request):
    f = FoodItemFilter(request.GET, queryset=FoodItem.objects.is_active().select_related())

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/food_item_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

class master_attribute_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = MasterAttribute
    def get_success_url(self):
        master_attribute = super(master_attribute_delete, self).get_object()
        mr_id = master_attribute.reference.id
        return reverse_lazy(
            'master_reference-detail',
            args=(mr_id,)
        )

def master_attribute_detail(request, pk):
    master_attribute = get_object_or_404(MasterAttribute, pk=pk, is_active=1)
    attribute_group = master_attribute.groups.first()
    return render(request, 'mb/master_attribute_detail.html', {'master_attribute': master_attribute, 'attribute_group' : attribute_group})

@login_required
@permission_required('mb.edit_master_attribute', raise_exception=True)
def master_attribute_edit(request, pk):
    master_attribute = get_object_or_404(MasterAttribute, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, master_attribute):
        raise PermissionDenied

    if request.method == "POST":
        form = MasterAttributeForm(request.POST, instance=master_attribute)
        if form.is_valid():
            master_attribute = form.save(commit=False)
            master_attribute.save()
            return redirect('master_attribute-detail', pk=master_attribute.pk)
    else:
        form = MasterAttributeForm(instance=master_attribute)
    return render(request, 'mb/master_attribute_edit.html', {'form': form})

def master_attribute_list(request):
    f = MasterAttributeFilter(request.GET, queryset=MasterAttribute.objects.is_active().filter(entity__name = 'Taxon').order_by('name'))

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    for x in page_obj:
        vars(x)['group']=x.groups.first()

    return render(
        request,
        'mb/master_attribute_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

@login_required
@permission_required('mb.add_choiceset_option', raise_exception=True)
def master_attribute_master_choiceset_option_new(request, master_attribute):
    master_attribute = get_object_or_404(MasterAttribute, pk=master_attribute, is_active=1)
    if request.method == "POST":
        form = MasterAttributeChoicesetOptionForm(request.POST)
        if form.is_valid():
            choiceset_option = form.save(commit=False)
            choiceset_option.master_attribute = master_attribute
            choiceset_option.save()
            return redirect('master_attribute-detail', pk=choiceset_option.master_attribute.id)
    else:
        form = MasterAttributeChoicesetOptionForm()
    return render(request, 'mb/master_attribute_master_choiceset_option_edit.html', {'form': form})

class master_choiceset_option_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = MasterChoiceSetOption
    def get_success_url(self):
        obj = super(master_choiceset_option_delete, self).get_object()
        ma_id = obj.master_attribute.id
        return reverse_lazy(
            'master_attribute-detail',
            args=(ma_id,)
        )

def master_choiceset_option_detail(request, pk):
    master_choiceset_option = get_object_or_404(MasterChoiceSetOption, pk=pk, is_active=1)
    return render(request, 'mb/master_choiceset_option_detail.html', {'master_choiceset_option': master_choiceset_option})

@login_required
@permission_required('mb.edit_master_choiceset_option', raise_exception=True)
def master_choiceset_option_edit(request, pk):
    master_choiceset_option = get_object_or_404(MasterChoiceSetOption, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, master_choiceset_option):
        raise PermissionDenied

    if request.method == "POST":
        form = MasterChoiceSetOptionForm(request.POST, instance=master_choiceset_option)
        if form.is_valid():
            master_choiceset_option = form.save(commit=False)
            master_choiceset_option.save()
            return redirect('master_choiceset_option-detail', pk=master_choiceset_option.pk)
    else:
        form = MasterChoiceSetOptionForm(instance=master_choiceset_option)
    return render(request, 'mb/master_choiceset_option_edit.html', {'form': form})

class master_entity_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = MasterEntity
    success_url = reverse_lazy('master_entity-list')

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def master_entity_detail(request, pk):
    master_entity = get_object_or_404(MasterEntity, pk=pk, is_active=1)
    with connection.cursor() as cursor:

#        cursor.execute("SELECT foo FROM bar WHERE baz = %s", [master_entity.id])
        cursor.execute("""
            select me.id master_entity_id
            , sum(ifnull(tp.time_in_months/12,1) /
              (select
               sum(ifnull(tp.time_in_months/12,1))
               from mb_dietset ds
               join mb_sourceentity se
            	  on se.id=ds.taxon_id and se.is_active=1
               join mb_entityrelation er
            	  on er.source_entity_id=se.id and er.is_active=1
            	  and er.relation_id=1
               join mb_masterentity e
            	  on e.id=er.master_entity_id and e.is_active=1
               join mb_sourcereference sr
            	  on sr.id=ds.reference_id and sr.is_active=1
               join mb_masterreference mr
            	  on mr.id=sr.master_reference_id and mr.is_active=1
               left join mb_timeperiod tp
            	  on tp.id=ds.time_period_id and tp.is_active=1
               where e.id=me.id and ds.is_active=1)
               *
               ((select COUNT(distinct z.list_order) FROM mb_dietsetitem z WHERE z.diet_set_id = ds.id and z.is_active=1)
               - dsi.list_order + 1 )
               /
               ((select COUNT(distinct z.list_order) FROM mb_dietsetitem z WHERE z.diet_set_id = ds.id and z.is_active=1)
               * ((select MIN(z.list_order) FROM mb_dietsetitem z WHERE z.diet_set_id = ds.id and z.is_active=1)
               + (select MAX(z.list_order) FROM mb_dietsetitem z WHERE z.diet_set_id = ds.id and z.is_active=1))
               / 2) * 100) sum_food_item_percentage
            , ifnull(sy.tsn_accepted, fi.tsn) tsn
            , tu.completename
            , group_concat(distinct fi.name SEPARATOR '; ') diet_items
            , part.caption part
            , group_concat(distinct sr.citation ORDER BY sr.citation SEPARATOR '; ') `references`

            from mb_dietset ds
            join mb_sourceentity se
            	on se.id=ds.taxon_id and se.is_active=1
            join mb_entityrelation er
            	on er.source_entity_id=se.id and er.relation_id=1 and er.is_active=1
            join mb_masterentity me
            	on me.id=er.master_entity_id and me.is_active=1
            join mb_sourcereference sr
            	on sr.id=ds.reference_id and sr.is_active=1
            join mb_masterreference mr
            	on mr.id=sr.master_reference_id and mr.is_active=1
            join mb_dietsetitem dsi
            	on dsi.diet_set_id=ds.id and dsi.is_active=1
            left join mb_fooditem fi
            	on fi.id=dsi.food_item_id and fi.is_active=1
            left join mb_sourcelocation sl
            	on sl.id=ds.location_id and sl.is_active=1
            left join mb_choicevalue gender
            	on gender.id=ds.gender_id and gender.is_active=1
            left join mb_sourcemethod sm
            	on sm.id=ds.method_id and sm.is_active=1
            left join mb_timeperiod tp
            	on tp.id=ds.time_period_id and tp.is_active=1
            left join mb_choicevalue part
            	on part.id=fi.part_id and part.is_active=1
            left join itis_taxonomicunits tu
            	on tu.tsn=fi.tsn
            left join itis_synonymlinks sy
            	on sy.tsn=fi.tsn
            where ds.is_active=1 and part.caption <> 'NONE' and me.id in (%s)
            group by me.id, ifnull(sy.tsn_accepted, fi.tsn), part.caption
            order by 1,2 desc
            """, [master_entity.id])

        diets = dictfetchall(cursor)

    with connection.cursor() as cursor:
#        cursor.execute("SELECT foo FROM bar WHERE baz = %s", [master_entity.id])
        cursor.execute("""
            select se.name source_taxon
                , ma.id master_attribute_id
                , ma.name master_attribute
            	, sl.name location
            	, smv.n_total
            	, smv.n_unknown
                , smv.n_female
            	, smv.n_male
            	, smv.minimum as minimum
            	, smv.minimum*uc.coefficient as coeff_minimum
            	, smv.mean as mean
            	, smv.mean*uc.coefficient as coeff_mean
            	, smv.maximum as maximum
            	, smv.maximum*uc.coefficient as coeff_maximum
            	, smv.std
            	, mu.print_name master_unit
            	, mr.citation reference
            from mb_masterentity me
            join mb_entityrelation er
            	on er.master_entity_id=me.id
            join mb_sourceentity se
            	on se.id=er.source_entity_id
            join mb_sourcereference sr
            	on sr.id=se.reference_id
            join mb_masterreference mr
            	on mr.id=sr.master_reference_id
            join mb_sourcemeasurementvalue smv
            	on smv.source_entity_id=se.id
            join mb_sourcelocation sl
            	on sl.id=smv.source_location_id
            join mb_sourceattribute sa
            	on sa.id=smv.source_attribute_id
            join mb_attributerelation ar
            	on ar.source_attribute_id=sa.id
            join mb_masterattribute ma
            	on ma.id=ar.master_attribute_id
            join mb_sourceunit su
            	on su.id=smv.source_unit_id
            join mb_unitrelation ur
            	on ur.source_unit_id=smv.source_unit_id
            join mb_masterunit u
            	on u.id=ur.master_unit_id
            join mb_masterunit mu
            	on mu.id=ma.unit_id
            left join mb_unitconversion uc
            	on uc.from_unit_id=u.id
            	and uc.to_unit_id=mu.id
            where me.id = %s
            order by ma.name""", [master_entity.id])

        measurements = dictfetchall(cursor)

# Begin Ternary plot data
    with connection.cursor() as cursor:
#        cursor.execute("SELECT foo FROM bar WHERE baz = %s", [master_entity.id])
        cursor.execute("""
        select me.id
        , me.name
        , dsd.n_ds
        , dsd.time_in_months
        , dsd.n_months
        , dsid.food_item_percentage
        , sum(dsd.time_in_months/dsd.n_months*dsid.food_item_percentage*dsid.cp_std) cp
        , sum(dsd.time_in_months/dsd.n_months*dsid.food_item_percentage*dsid.ee_std) ee
        , sum(dsd.time_in_months/dsd.n_months*dsid.food_item_percentage*dsid.cf_std) cf
        , sum(dsd.time_in_months/dsd.n_months*dsid.food_item_percentage*dsid.ash_std) ash
        , sum(dsd.time_in_months/dsd.n_months*dsid.food_item_percentage*dsid.nfe_std) nfe
        from mb_masterentity me
        join mb_entityrelation er
        on er.master_entity_id=me.id and er.relation_id=1 and er.is_active=1
        join mb_dietset ds
        on ds.taxon_id=er.source_entity_id and ds.is_active=1
        join mb_table_dietset_data dsd
        on dsd.ds_id=ds.id
        join mb_table_dietsetitem_data dsid
        on dsid.diet_set_id=ds.id
        where me.is_active=1 and me.id = %s
        group by me.id""", [master_entity.id])

        ternary = dictfetchall(cursor)

#https://www.codingwithricky.com/2019/08/28/easy-django-plotly/
#https://community.plotly.com/t/how-to-add-a-polygon-and-a-caption-for-it-on-a-ternary-plot/47268
    if ternary:
        cf_ash = ternary[0]['cf']+ternary[0]['ash']
        nfe = ternary[0]['nfe']
        cp_ee = ternary[0]['cp']+ternary[0]['ee']
    else:
        cf_ash = 1.0
        nfe = 0.0
        cp_ee = 0.0

    data = [[cf_ash, nfe, cp_ee]]
    df = PandasDataFrame(data,columns=['CF+ASH','NFE','CP+EE'])
    fig = plotly_express.scatter_ternary(df, a="CF+ASH", b="NFE", c="CP+EE")

# Animalivory
    t = [0.0, 0.0, 0.1, 0.2, 0.2]
    l = [0.0, 0.3, 0.3, 0.2, 0.0]
    r = [1.0, 0.7, 0.6, 0.6, 0.8]
    fig.add_scatterternary(a=t, b=l, c=r, name="",
                            mode='lines', fill="toself", text="Animalivory", showlegend=False)
# Herbivory
    t = [0.3, 0.5, 0.5, 0.4]
    l = [0.5, 0.5, 0.4, 0.4]
    r = [0.2, 0.0, 0.1, 0.2]
    fig.add_scatterternary(a=t, b=l, c=r, name="",
                            mode='lines', fill="toself", text="Herbivory", showlegend=False)

# Frugivory
    t = [0.0, 0.0, 0.3, 0.3, 0.2]
    l = [0.7, 1.0, 0.7, 0.5, 0.5]
    r = [0.3, 0.0, 0.0, 0.2, 0.3]
    fig.add_scatterternary(a=t, b=l, c=r, name="",
                            mode='lines', fill="toself", text="Frugivory", showlegend=False)

# Omnivory
    t = [0.0, 0.0, 0.3, 0.3, 0.2]
    l = [0.4, 0.65, 0.35, 0.2, 0.2]
    r = [0.6, 0.35, 0.35, 0.5, 0.6]
    fig.add_scatterternary(a=t, b=l, c=r, name="",
                            mode='lines', fill="toself", text="Omnivory", showlegend=False)

    plot_div = plotly_offline_plot(fig, output_type='div', include_plotlyjs=False, show_link=False, link_text="")

    return render(request, 'mb/master_entity_detail.html', {'master_entity': master_entity, 'measurements': measurements, 'diets': diets, 'ternary':ternary, 'plot_div': plot_div,})

@login_required
@permission_required('mb.edit_master_entity', raise_exception=True)
def master_entity_edit(request, pk):
    master_entity = get_object_or_404(MasterEntity, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, master_entity):
        raise PermissionDenied

    if request.method == "POST":
        form = MasterEntityForm(request.POST, instance=master_entity)
        if form.is_valid():
            master_entity = form.save(commit=False)
            master_entity.save()
            return redirect('master_entity-detail', pk=master_entity.pk)
    else:
        form = MasterEntityForm(instance=master_entity)
    return render(request, 'mb/master_entity_edit.html', {'form': form})

def master_entity_list(request):
    f = MasterEntityFilter(request.GET, queryset=MasterEntity.objects.is_active().filter(reference_id=4).filter(entity__name = 'Species').order_by('name'))

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/master_entity_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

def master_entity_reference_list(request):
    f = MasterReferenceFilter(request.GET, queryset=MasterReference.objects
        .is_active()
        .filter(sourcereference__sourceattribute__type__gte=0)
        .distinct())

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/master_entity_reference_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

class master_reference_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = MasterReference
    success_url = reverse_lazy('master_reference-list')

def master_reference_detail(request, pk):
    master_reference = get_object_or_404(MasterReference, pk=pk, is_active=1)
    with connection.cursor() as cursor:
        cursor.execute("""
            select case when se.name=me.name then me.name else concat(me.name,' (',se.name,')') end taxon
            , case when source.name=`master`.name then `master`.name else concat(`master`.name,' (',source.name,')') end rank
            , data_status.name data_status, relation_status.name relation_status
            , me.id master_entity_id
            from mb_masterreference mr
            join mb_sourcereference sr
            	on sr.master_reference_id=mr.id
            join mb_sourceentity se
            	on se.reference_id=sr.id
            	and se.entity_id in(1,3,4,5,7,10,11,12,13,14,15)
            join mb_entityclass source
            	on se.entity_id=source.id
            join mb_entityrelation er
            	on er.source_entity_id=se.id
            join mb_masterentity me
            	on me.id=er.master_entity_id
            join mb_entityclass `master`
            	on me.entity_id=`master`.id
            join mb_relationclass relation
            	on relation.id=er.relation_id
            	and relation.name='Taxon Match'
            join mb_masterchoicesetoption data_status
            	on data_status.id=er.data_status_id
            join mb_masterchoicesetoption relation_status
            	on relation_status.id=er.relation_status_id
           where mr.id = %s""", [master_reference.id])
        taxa = dictfetchall(cursor)

    with connection.cursor() as cursor:
        cursor.execute("""
		select sa.id source_attribute_id, sa.name source_attribute, ma.id master_attribute_id, ma.name master_attribute
		from mb_masterreference mr
		join mb_sourcereference sr
			on sr.master_reference_id=mr.id
		join	mb_sourceattribute sa
			on sa.reference_id=sr.id
		left join mb_attributerelation ar
			on ar.source_attribute_id=sa.id
		left join mb_masterattribute ma
			on ma.id=ar.master_attribute_id
		where mr.id=%s
		order by ma.name
        """, [master_reference.id])
        attributes = dictfetchall(cursor)

    return render(request, 'mb/master_reference_detail.html'
        , {'master_reference': master_reference, 'taxa': taxa, 'attributes': attributes, })

@login_required
@permission_required('mb.edit_master_reference', raise_exception=True)
def master_reference_edit(request, pk):
    master_reference = get_object_or_404(MasterReference, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, master_reference):
        raise PermissionDenied

    if request.method == "POST":
        form = MasterReferenceForm(request.POST, instance=master_reference)
        if form.is_valid():
            master_reference = form.save(commit=False)
            master_reference.save()
            return redirect('master_reference-detail', pk=master_reference.pk)
    else:
        form = MasterReferenceForm(instance=master_reference)
    return render(request, 'mb/master_reference_edit.html', {'form': form})

#def master_reference_list(request):
#    f = MasterReferenceFilter(request.GET, queryset=MasterReference.objects.is_active())

#    paginator = Paginator(f.qs, 10)

#    page_number = request.GET.get('page')
#    try:
#        page_obj = paginator.page(page_number)
#    except PageNotAnInteger:
#        page_obj = paginator.page(1)
#    except EmptyPage:
#        page_obj = paginator.page(paginator.num_pages)

#    return render(
#        request,
#        'mb/master_reference_list.html',
#        {'page_obj': page_obj, 'filter': f,}
#    )

class proximate_analysis_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = ProximateAnalysis
    success_url = reverse_lazy('proximate_analysis-list')

def proximate_analysis_detail(request, pk):
    proximate_analysis = get_object_or_404(ProximateAnalysis, pk=pk, is_active=1)
    return render(request, 'mb/proximate_analysis_detail.html', {'proximate_analysis': proximate_analysis})

@login_required
@permission_required('mb.edit_proximate_analysis', raise_exception=True)
def proximate_analysis_edit(request, pk):
    proximate_analysis = get_object_or_404(ProximateAnalysis, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, proximate_analysis):
        raise PermissionDenied

    if request.method == "POST":
        form = ProximateAnalysisForm(request.POST, instance=proximate_analysis)
        if form.is_valid():
            proximate_analysis = form.save(commit=False)
            proximate_analysis.save()
            return redirect('proximate_analysis-detail', pk=proximate_analysis.pk)
    else:
        form = ProximateAnalysisForm(instance=proximate_analysis)
    return render(request, 'mb/proximate_analysis_edit.html', {'form': form})

def proximate_analysis_list(request):
    f = ProximateAnalysisFilter(request.GET, queryset=ProximateAnalysis.objects.is_active().select_related())

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/proximate_analysis_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

class proximate_analysis_item_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = ProximateAnalysisItem
    success_url = reverse_lazy('proximate_analysis_item-list')

def proximate_analysis_item_detail(request, pk):
    proximate_analysis_item = get_object_or_404(ProximateAnalysisItem, pk=pk, is_active=1)
    return render(request, 'mb/proximate_analysis_item_detail.html', {'proximate_analysis_item': proximate_analysis_item})

@login_required
@permission_required('mb.edit_proximate_analysis_item', raise_exception=True)
def proximate_analysis_item_edit(request, pk):
    proximate_analysis_item = get_object_or_404(ProximateAnalysisItem, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, proximate_analysis_item):
        raise PermissionDenied

    if request.method == "POST":
        form = ProximateAnalysisItemForm(request.POST, instance=proximate_analysis_item)
        if form.is_valid():
            proximate_analysis_item = form.save(commit=False)
            std_values = generate_standard_values_pa(form.cleaned_data)
            proximate_analysis_item.cp_std = std_values['cp_std']
            proximate_analysis_item.ee_std = std_values['ee_std']
            proximate_analysis_item.cf_std = std_values['cf_std']
            proximate_analysis_item.ash_std = std_values['ash_std']
            proximate_analysis_item.nfe_std = std_values['nfe_std']
            proximate_analysis_item.save()
            return redirect('proximate_analysis_item-detail', pk=proximate_analysis_item.pk)
    else:
        form = ProximateAnalysisItemForm(instance=proximate_analysis_item)
    return render(request, 'mb/proximate_analysis_item_edit.html', {'form': form})

def proximate_analysis_item_list(request):
    f = ProximateAnalysisItemFilter(request.GET, queryset=ProximateAnalysisItem.objects.is_active().select_related())

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/proximate_analysis_item_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

def proximate_analysis_reference_detail(request, pk):
    master_reference = get_object_or_404(MasterReference, pk=pk, is_active=1)

    return render(request, 'mb/proximate_analysis_reference_detail.html'
        , {'master_reference': master_reference, })

def proximate_analysis_reference_list(request):
    f = MasterReferenceFilter(request.GET, queryset=MasterReference.objects
        .is_active()
        .filter(sourcereference__proximateanalysis__gte=0)
        .distinct())

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/proximate_analysis_reference_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

class source_attribute_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = SourceAttribute
    def get_success_url(self):
        source_attribute = super(source_attribute_delete, self).get_object()
        sr_id = source_attribute.reference.id
        return reverse_lazy(
            'source_reference-detail',
            args=(sr_id,)
        )

def source_attribute_detail(request, pk):
    source_attribute = get_object_or_404(SourceAttribute, pk=pk, is_active=1)
    return render(request, 'mb/source_attribute_detail.html', {'source_attribute': source_attribute})

@login_required
@permission_required('mb.edit_source_attribute', raise_exception=True)
def source_attribute_edit(request, pk):
    source_attribute = get_object_or_404(SourceAttribute, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, source_attribute):
        raise PermissionDenied

    if request.method == "POST":
        form = SourceAttributeForm(request.POST, instance=source_attribute)
        if form.is_valid():
            source_attribute = form.save(commit=False)
            source_attribute.save()
            return redirect('source_attribute-detail', pk=source_attribute.pk)
    else:
        form = SourceAttributeForm(instance=source_attribute)
    return render(request, 'mb/source_attribute_edit.html', {'form': form})

def source_attribute_list(request):
    f = SourceAttributeFilter(request.GET, queryset=SourceAttribute.objects.is_active().order_by('name'))

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/source_attribute_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

@login_required
@permission_required('mb.add_choiceset_option', raise_exception=True)
def source_attribute_source_choiceset_option_new(request, source_attribute):
    source_attribute = get_object_or_404(SourceAttribute, pk=source_attribute, is_active=1)
    if request.method == "POST":
        form = SourceAttributeChoicesetOptionForm(request.POST)
        if form.is_valid():
            choiceset_option = form.save(commit=False)
            choiceset_option.source_attribute = source_attribute
            choiceset_option.save()
            return redirect('source_attribute-detail', pk=choiceset_option.source_attribute.id)
    else:
        form = SourceAttributeChoicesetOptionForm()
    return render(request, 'mb/source_attribute_source_choiceset_option_edit.html', {'form': form})

class source_choiceset_option_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = SourceChoiceSetOption
    def get_success_url(self):
        obj = super(source_choiceset_option_delete, self).get_object()
        sa_id = obj.source_attribute.id
        return reverse_lazy(
            'source_attribute-detail',
            args=(sa_id,)
        )

def source_choiceset_option_detail(request, pk):
    source_choiceset_option = get_object_or_404(SourceChoiceSetOption, pk=pk, is_active=1)
    return render(request, 'mb/source_choiceset_option_detail.html', {'source_choiceset_option': source_choiceset_option})

@login_required
@permission_required('mb.edit_source_choiceset_option', raise_exception=True)
def source_choiceset_option_edit(request, pk):
    source_choiceset_option = get_object_or_404(SourceChoiceSetOption, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, source_choiceset_option):
        raise PermissionDenied

    if request.method == "POST":
        form = SourceChoiceSetOptionForm(request.POST, instance=source_choiceset_option)
        if form.is_valid():
            source_choiceset_option = form.save(commit=False)
            source_choiceset_option.save()
            return redirect('source_choiceset_option-detail', pk=source_choiceset_option.pk)
    else:
        form = SourceChoiceSetOptionForm(instance=source_choiceset_option)
    return render(request, 'mb/source_choiceset_option_edit.html', {'form': form})

class source_choiceset_option_value_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = SourceChoiceSetOptionValue
    def get_success_url(self):
        obj = super(source_choiceset_option_value_delete, self).get_object()
        source_entity_id = obj.source_entity.id
        return reverse_lazy(
            'source_entity-detail',
            args=(source_entity_id,)
        )

def source_choiceset_option_value_detail(request, pk):
    source_choiceset_option_value = get_object_or_404(SourceChoiceSetOptionValue, pk=pk, is_active=1)
    return render(request, 'mb/source_choiceset_option_value_detail.html', {'source_choiceset_option_value': source_choiceset_option_value})

@login_required
@permission_required('mb.edit_source_choiceset_option_value', raise_exception=True)
def source_choiceset_option_value_edit(request, pk):
    source_choiceset_option_value = get_object_or_404(SourceChoiceSetOptionValue, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, source_choiceset_option_value):
        raise PermissionDenied

    sac = source_choiceset_option_value.source_choiceset_option.source_attribute.id
    if request.method == "POST":
        form = SourceChoiceSetOptionValueForm(request.POST, instance=source_choiceset_option_value, sac=sac)
        if form.is_valid():
            source_choiceset_option_value = form.save(commit=False)
            source_choiceset_option_value.save()
            return redirect('source_entity-detail', pk=source_choiceset_option_value.source_entity.id)
    else:
        form = SourceChoiceSetOptionValueForm(instance=source_choiceset_option_value, sac=sac)
#        form = SourceChoiceSetOptionValueForm()
    return render(request, 'mb/source_choiceset_option_value_edit.html', {'form': form})

@login_required
@permission_required('mb.add_source_choiceset_option_value', raise_exception=True)
def source_choiceset_option_value_new(request, se, sac):
    source_entity = get_object_or_404(SourceEntity, pk=se)
    if request.method == "POST":
        form = SourceChoiceSetOptionValueForm(request.POST, sac=sac)
        if form.is_valid():
            source_choiceset_option_value = form.save(commit=False)
            source_choiceset_option_value.source_entity = source_entity
            source_choiceset_option_value.save()
            return redirect('source_entity-detail', pk=source_choiceset_option_value.source_entity.id)
    else:
        form = SourceChoiceSetOptionValueForm(sac=sac)
    return render(request, 'mb/source_choiceset_option_value_edit.html', {'form': form})

@login_required
@permission_required('mb.add_source_attribute', raise_exception=True)
def source_entity_attribute_new(request, source_reference, source_entity):
    reference = get_object_or_404(SourceReference, pk=source_reference, is_active=1)
    if request.method == "POST":
        form = SourceReferenceAttributeForm(request.POST)
        if form.is_valid():
            source_attribute = form.save(commit=False)
            source_attribute.reference = reference
            source_attribute.type = 2
            source_attribute.save()
            return redirect('source_entity-detail', pk=source_entity)
    else:
        form = SourceReferenceAttributeForm()
    return render(request, 'mb/source_reference_attribute_edit.html', {'form': form})

@login_required
@permission_required('mb.add_source_attribute', raise_exception=True)
def source_entity_measurement_new(request, source_reference, source_entity):
    reference = get_object_or_404(SourceReference, pk=source_reference, is_active=1)
    if request.method == "POST":
        form = SourceReferenceAttributeForm(request.POST)
        if form.is_valid():
            source_attribute = form.save(commit=False)
            source_attribute.reference = reference
            source_attribute.type = 1
            source_attribute.save()
            return redirect('source_entity-detail', pk=source_entity)
    else:
        form = SourceReferenceAttributeForm()
    return render(request, 'mb/source_reference_measurement_edit.html', {'form': form})

class source_entity_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = SourceEntity
    success_url = reverse_lazy('source_entity-list')

def source_entity_detail(request, pk):
    source_entity = get_object_or_404(SourceEntity, pk=pk, is_active=1)
    source_reference = get_object_or_404(SourceReference, pk=source_entity.reference.id)
    sa_ids = SourceAttribute.objects.is_active().filter(reference = source_reference).values('id')
    sa_has_values = (SourceChoiceSetOptionValue
        .objects
        .is_active()
        .filter(source_choiceset_option__source_attribute__type = 2)
        .filter(source_choiceset_option__source_attribute__in=sa_ids)
        .filter(source_entity = source_entity))
    sa_no_values = (SourceAttribute
        .objects
        .is_active()
        .filter(type = 2)
        .filter(reference = source_reference)
        .exclude(pk__in=sa_has_values.values('source_choiceset_option__source_attribute_id')))
    sa_has_measurements = (SourceMeasurementValue
        .objects
        .is_active()
        .filter(source_attribute__type = 1)
        .filter(source_attribute__in = sa_ids)
        .filter(source_entity = source_entity))
    sa_no_measurements = (SourceAttribute
        .objects
        .is_active()
        .filter(type = 1)
        .filter(reference = source_reference)
        .exclude(pk__in = sa_has_measurements.values('source_attribute_id')))

    return render(request, 'mb/source_entity_detail.html'
        , {'source_entity': source_entity
        , 'sa_has_values': sa_has_values
        , 'sa_no_values': sa_no_values
        , 'sa_has_measurements': sa_has_measurements
        , 'sa_no_measurements': sa_no_measurements
        ,})

def source_entity_list(request):
    f = SourceEntityFilter(request.GET, queryset=SourceEntity.objects.is_active().order_by('name'))

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/source_entity_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

@login_required
@permission_required('mb.edit_source_entity', raise_exception=True)
def source_entity_edit(request, pk):
    source_entity = get_object_or_404(SourceEntity, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, source_entity):
        raise PermissionDenied

    if request.method == "POST":
        form = SourceEntityForm(request.POST, instance=source_entity)
        if form.is_valid():
            source_entity = form.save(commit=False)
            source_entity.save()
            return redirect('source_entity-detail', pk=source_entity.pk)
    else:
        form = SourceEntityForm(instance=source_entity)
    return render(request, 'mb/source_entity_edit.html', {'form': form})

@login_required
@permission_required('mb.add_relation', raise_exception=True)
def source_entity_relation_new(request, source_entity):
    source_entity = get_object_or_404(SourceEntity, pk=source_entity, is_active=1)
    er_relation = get_object_or_404(RelationClass, pk=1, is_active=1)
    if request.method == "POST":
        form = SourceEntityRelationForm(request.POST)
        if form.is_valid():
            relation = form.save(commit=False)
            relation.relation = er_relation
            relation.source_entity = source_entity
            relation.save()
            return redirect('source_entity-detail', pk=relation.source_entity.id)
    else:
        form = SourceEntityRelationForm()
    return render(request, 'mb/source_entity_relation_edit.html', {'form': form})

class source_measurement_value__delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = SourceMeasurementValue
    def get_success_url(self):
        obj = super(source_measurement_value__delete, self).get_object()
        source_entity_id = obj.source_entity.id
        return reverse_lazy(
            'source_entity-detail',
            args=(source_entity_id,)
        )

@login_required
@permission_required('mb.read_source_measurement_value', raise_exception=True)
def source_measurement_value_detail(request, pk):
    source_measurement_value = get_object_or_404(SourceMeasurementValue, pk=pk, is_active=1)
    if not user_is_data_admin_or_owner(request.user, source_measurement_value):
        raise PermissionDenied

    return render(request, 'mb/source_measurement_value_detail.html', {'source_measurement_value': source_measurement_value})

@login_required
@permission_required('mb.edit_source_measurement_value', raise_exception=True)
def source_measurement_value_edit(request, pk):
    source_measurement_value = get_object_or_404(SourceMeasurementValue, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, source_measurement_value):
        raise PermissionDenied

    sa = source_measurement_value.source_attribute.id
    if request.method == "POST":
        form = SourceMeasurementValueForm(request.POST, instance=source_measurement_value)
        if form.is_valid():
            source_measurement_value = form.save(commit=False)
            source_measurement_value.save()
            return redirect('source_entity-detail', pk=source_measurement_value.source_entity.id)
    else:
        form = SourceMeasurementValueForm(instance=source_measurement_value)
    return render(request, 'mb/source_measurement_value_edit.html', {'form': form})

@login_required
@permission_required('mb.add_source_measurement_value', raise_exception=True)
def source_measurement_value_new(request, sa, se):
    source_attribute = get_object_or_404(SourceAttribute, pk=sa)
    source_entity = get_object_or_404(SourceEntity, pk=se)
    if request.method == "POST":
        form = SourceMeasurementValueForm(request.POST)
        if form.is_valid():
            source_measurement_value = form.save(commit=False)
            source_measurement_value.source_attribute = source_attribute
            source_measurement_value.source_entity = source_entity
            source_measurement_value.save()
            return redirect('source_entity-detail', pk=source_measurement_value.source_entity.id)
    else:
        form = SourceMeasurementValueForm()
    return render(request, 'mb/source_measurement_value_edit.html', {'form': form})

class source_reference_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = SourceReference
    success_url = reverse_lazy('source_reference-list')

@login_required
@permission_required('mb.add_source_reference', raise_exception=True)
def source_reference_new(request):
    if request.method == "POST":
        form = SourceReferenceForm(request.POST)
        if form.is_valid():
            source_reference = form.save(commit=False)
            source_reference.save()
            return redirect('source_reference-detail', pk=source_reference.pk)
    else:
        form = SourceReferenceForm()
    return render(request, 'mb/source_reference_edit.html', {'form': form})

@login_required
@permission_required('mb.add_source_attribute', raise_exception=True)
def source_reference_attribute_new(request, source_reference, type):
    reference = get_object_or_404(SourceReference, pk=source_reference, is_active=1)
    if request.method == "POST":
        form = SourceReferenceAttributeForm(request.POST)
        if form.is_valid():
            source_attribute = form.save(commit=False)
            source_attribute.reference = reference
            source_attribute.entity_id = 2
            source_attribute.type = type
            source_attribute.save()
            return redirect('source_reference-detail', pk=source_attribute.reference.id)
    else:
        form = SourceReferenceAttributeForm()
    return render(request, 'mb/source_reference_attribute_edit.html', {'form': form})

def source_reference_detail(request, pk):

    source_reference = get_object_or_404(SourceReference
        .objects
        .is_active()
        .select_related('master_reference'), pk=pk
        )

    sr_traits = (SourceAttribute
        .objects
        .is_active()
        .filter(type = 2)
        .filter(reference = source_reference)
        .select_related('entity',)
        .prefetch_related('attributerelation_set__master_attribute',)
        .order_by('name')
        )

    sr_measurements = (SourceAttribute
        .objects
        .is_active()
        .filter(type = 1)
        .filter(reference = source_reference)
        .select_related('entity').order_by('name')
        )

    sr_diet_sets = (DietSet
        .objects
        .is_active()
        .filter(reference = source_reference)
        )

    with connection.cursor() as cursor:
        cursor.execute("""
			select
				se.reference_id
				, se.id source_entity_id
				, se.name source_entity_name
				, sec.name source_entity_rank
				, me.id master_entity_id
				, me.name master_entity_name
				, mec.name master_entity_rank
				, relation_status.name match_type
                , data_status.name data_status
				, mr.citation
			from mb_sourceentity se
			left join mb_entityclass sec
				on sec.id=se.entity_id
			left join mb_entityrelation er
				on er.source_entity_id=se.id
			left join mb_relationclass rc
				on rc.id=er.relation_id
				and rc.name='TaxonMatch'
			left join mb_masterchoicesetoption relation_status
				on relation_status.id=er.relation_status_id
            left join mb_masterchoicesetoption data_status
                on data_status.id=er.data_status_id
			left join mb_masterentity me
				on me.id=er.master_entity_id
			left join mb_entityclass mec
				on mec.id=me.entity_id
			left join mb_masterreference mr
				on me.reference_id=mr.id
			where se.reference_id=%s
			order by se.name""", [source_reference.id])

        sr_entities = dictfetchall(cursor)

    return render(request, 'mb/source_reference_detail.html'
        , {'source_reference': source_reference
        , 'sr_traits': sr_traits
        , 'sr_measurements': sr_measurements
        , 'sr_diet_sets': sr_diet_sets
        , 'sr_entities': sr_entities
        ,})

@login_required
@permission_required('mb.edit_source_reference', raise_exception=True)
def source_reference_edit(request, pk):
    source_reference = get_object_or_404(SourceReference, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, source_reference):
        raise PermissionDenied

    if request.method == "POST":
        form = SourceReferenceForm(request.POST, instance=source_reference)
        if form.is_valid():
            source_reference = form.save(commit=False)
            source_reference.save()
            return redirect('source_reference-detail', pk=source_reference.pk)
    else:
        form = SourceReferenceForm(instance=source_reference)
    return render(request, 'mb/source_reference_edit.html', {'form': form})

def source_reference_list(request):
    f = SourceReferenceFilter(request.GET, queryset=SourceReference.objects.is_active().order_by('citation'))

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/source_reference_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

class time_period_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = TimePeriod
    success_url = reverse_lazy('time_period-list')

def time_period_detail(request, pk):
    time_period = get_object_or_404(TimePeriod, pk=pk, is_active=1)
    return render(request, 'mb/time_period_detail.html', {'time_period': time_period})

@login_required
@permission_required('mb.edit_time_period', raise_exception=True)
def time_period_edit(request, pk):
    time_period = get_object_or_404(TimePeriod, pk=pk, is_active=1)

    if not user_is_data_admin_or_owner(request.user, time_period):
        raise PermissionDenied

    if request.method == "POST":
        form = TimePeriodForm(request.POST, instance=time_period)
        if form.is_valid():
            time_period = form.save(commit=False)
            time_period.save()
            return redirect('time_period-detail', pk=time_period.pk)
    else:
        form = TimePeriodForm(instance=time_period)
    return render(request, 'mb/time_period_edit.html', {'form': form})

def time_period_list(request):
    f = TimePeriodFilter(request.GET, queryset=TimePeriod.objects.is_active().order_by('name'))

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/time_period_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

class tsn_delete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return user_is_data_admin_or_owner(self.request.user, self.get_object())
    model = TaxonomicUnits
    success_url = reverse_lazy('tsn-list')

def tsn_update(request, tsn):
    accepted_tsn=tsn
    kingdom_id = 0
    rank_id = 0

    taxonomic_unit = get_object_or_404(TaxonomicUnits, tsn=tsn)
    r1 = getTaxonomicRankNameFromTSN(tsn)
    if r1['kingdomId'] is None:
        kingdom_id = r1['kingdomId']
        rank_id = r1['rankId']

#    response1 = requests.get("https://www.itis.gov/ITISWebService/jsonservice/getTaxonomicRankNameFromTSN?tsn="+str(taxonomic_unit.tsn))

    response2 = GetAcceptedNamesfromTSN(taxonomic_unit.tsn)
    if response2['acceptedNames'] is None:
        accepted_tsn = tsn
    response3 = requests.get("https://www.itis.gov/ITISWebService/jsonservice/getFullHierarchyFromTSN?tsn="+str(taxonomic_unit.tsn))
#    r1 = response1.json()
    r3 = response3.json()
    strings1 = []
    strings3 = []
    strings4 = []

    i=0
    while r3['hierarchyList']:
        strings1.append(r3['hierarchyList'][i]['tsn'])
        strings3.append(r3['hierarchyList'][i]['taxonName'])
        if r3['hierarchyList'][i]['tsn'] == str(taxonomic_unit.tsn):
            break
        i += 1

    hierarchy_string = '-'.join(strings1)
    hierarchy = '-'.join(strings3)
    if len(hierarchy_string) > 0:
        taxonomic_unit.hierarchy_string = hierarchy_string
    else:
        taxonomic_unit.hierarchy_string = ''
    if len(hierarchy) > 0:
        taxonomic_unit.hierarchy = hierarchy
    else:
        taxonomic_unit.hierarchy = ''


    tsn_hierarchy = taxonomic_unit.hierarchy_string.split("-")
    i=len(tsn_hierarchy)-1
    found=False
    while(i>=0 and found is False):
        pa=ViewProximateAnalysisTable.objects.filter(tsn__hierarchy_string__endswith=tsn_hierarchy[i])
        if len(pa)>=1:
            break
        i=i-1

    taxonomic_unit.common_names = GetCommonNamesfromTSN(tsn)
    if kingdom_id != '0':
        taxonomic_unit.kingdom_id = kingdom_id
        taxonomic_unit.rank_id = rank_id
        taxonomic_unit.tsn_update_date = datetime.datetime.now()
        taxonomic_unit.save()

    return render(request, 'mb/tsn_detail.html', {'pa': pa, 'tsn': taxonomic_unit},)

def tsn_detail(request, tsn):
    taxonomic_unit = get_object_or_404(TaxonomicUnits, tsn=tsn)
    tsn_hierarchy = taxonomic_unit.hierarchy_string.split("-")
    pa = None
    for i in reversed(range(len(tsn_hierarchy))):
        if tsn_hierarchy[i] == "":
            break
        pa=ViewProximateAnalysisTable.objects.filter(tsn__hierarchy_string__endswith=tsn_hierarchy[i])
        if len(pa)>=1:
            break
    return render(request, 'mb/tsn_detail.html', {'pa': pa, 'tsn': taxonomic_unit},)

@login_required
def tsn_edit(request, tsn):
    tsn = get_object_or_404(TaxonomicUnits, tsn=tsn)

    if not user_is_data_admin_or_contributor(request.user, tsn):
        raise PermissionDenied

    if request.method == "POST":
        form = TaxonomicUnitsForm(request.POST, instance=tsn)
        if form.is_valid():
            tsn = form.save(commit=False)
            tsn.save()
            return redirect('tsn-detail', tsn=tsn.tsn)
    else:
        form = TaxonomicUnitsForm(instance=tsn)
    return render(request, 'mb/tsn_edit.html', {'form': form})

def tsn_list(request):
    f = TaxonomicUnitsFilter(request.GET, queryset=TaxonomicUnits.objects.all().select_related())

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/tsn_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

@login_required
@permission_required('mb.add_tsn', raise_exception=True)
def tsn_new(request):
    if request.method == "POST":

        form = TaxonomicUnitsForm(request.POST)
        if form.is_valid():
            tsn = form.save(commit=False)
            tsn.save()
            return redirect('tsn-detail', tsn=tsn.pk)
    else:
        form = TaxonomicUnitsForm()
    return render(request, 'mb/tsn_edit.html', {'form': form})

@login_required
@permission_required('mb.add_tsn', raise_exception=True)
def tsn_search(request):
    if request.method == "POST":

        tsn_data = json.loads(request.POST.get("tsn_data"))

        return_data = create_return_data(tsn_data["tsn"], tsn_data["scientificName"], status=tsn_data["nameUsage"])

        create_tsn(return_data, tsn_data["tsn"])
        return JsonResponse("recieved", safe=False, status=201)

    elif request.method == "GET":
        return_data = {"message":"Found no entries"}
        query = request.GET.get("query").lower().capitalize().replace(' ', '%20')
        url = 'http://www.itis.gov/ITISWebService/jsonservice/getITISTermsFromScientificName?srchKey=' + query
        try:
            session = CachedSession(ITIS_CACHE, expire_after=datetime.timedelta(days=1))
            file = session.get(url)
            data = file.text
        except Exception:
            return JsonResponse({"message":"Connection to ITIS failed."}, safe=False, status=200 )
        try:
            data = json.loads(data)['itisTerms']
        except UnicodeDecodeError:
            data = json.loads(data.decode('utf-8', 'ignore'))['itisTerms']

        if data[0] is not None:
            return_data["message"] = f"Found {len(data)} entries"
            for item in enumerate(data):
                item = item[1]
                return_data[item["tsn"]] = item
        return JsonResponse(return_data, safe=False, status=200 )

def view_proximate_analysis_table_list(request):
    f = ViewProximateAnalysisTableFilter(request.GET, queryset=ViewProximateAnalysisTable.objects.all().select_related())

    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        'mb/view_proximate_analysis_table_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

def get_occurrences_by_masterlocation(ml : MasterLocation):
    """
    Return occurrences by master location.
    """

    def remove_nan_value(string : str):
        """ Cut 'nan'-string. """
        return string.replace("nan", "")
    
    def get_master_entity(source_entity : SourceEntity):
        """ Get master entity by source entity. """
        master_entity = None
        try:
            master_entity = MasterEntity.objects.filter(source_entity=source_entity)[0]
        except Exception as e:
            print("virhe: " + str(e))
        return master_entity
    
    def get_source_habitat(event : Event):
        """ Get source habitat by event """
        source_habitat = event.source_habitat
        if source_habitat.habitat_type == "nan":
            return ""
        return source_habitat.habitat_type
    
    occurrences = []
    source_locations = []

    class OccurrenceView(models.Model):
        """ 'Tool model' to present a single occurrence with correct information. """
        event = models.CharField(max_length=500) 
        master_entity = models.CharField(max_length=500) 
        organism_quantity = models.CharField(max_length=500) 
        organism_quantity_type = models.CharField(max_length=500) 
        gender = models.CharField(max_length=500) 
        life_stage = models.CharField(max_length=500) 
        occurrence_remarks = models.CharField(max_length=500) 
        reference = models.CharField(max_length=500) 
        associated_references = models.CharField(max_length=500) 

    try:
        location_relations = LocationRelation.objects.filter(master_location=ml)
        
        for location_relation in location_relations:
            source_locations.append(location_relation.source_location)

        for source_location in source_locations:
            try:
                occs = Occurrence.objects.filter(source_location=source_location)
                for occ in occs:
                    gender = str(occ.gender).replace("Gender - ", "")
                    if gender == "None":
                        gender = ""

                    life_stage = str(occ.life_stage).replace("LifeStage - ", "")
                    if life_stage == "None":
                        life_stage = ""

                    reference = str(occ.source_reference)
                    if reference == "None":
                        reference = ""

                    master_entity = str(get_master_entity(occ.source_entity))
                    if master_entity == "None":
                        master_entity = ""

                    source_habitat = str(get_source_habitat(occ.event))

                    occ_view = OccurrenceView(event=source_habitat, master_entity=master_entity, organism_quantity=occ.organism_quantity,
                                              organism_quantity_type=occ.organism_quantity_type, gender=gender, life_stage=life_stage,
                                              occurrence_remarks=occ.occurrence_remarks, reference=reference, associated_references=occ.associated_references)
                    
                    occ_view.organism_quantity = remove_nan_value(occ_view.organism_quantity)
                    occ_view.organism_quantity_type = remove_nan_value(occ_view.organism_quantity_type)
                    occ_view.associated_references = remove_nan_value(occ_view.associated_references)
                    occ_view.occurrence_remarks = remove_nan_value(occ_view.occurrence_remarks)
                    
                    occurrences.append(occ_view)
            except Exception as e:
                print("virhe occurrence " + str(e))
                continue
    except Exception as e:
        print("error: " + str(e))
        return None
    
    if len(occurrences) == 0:
        return False
    
    return occurrences
