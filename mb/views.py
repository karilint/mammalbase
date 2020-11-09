import datetime
from django.db import connection
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .filters import (DietSetFilter, FoodItemFilter
    , MasterAttributeFilter, MasterEntityFilter, MasterReferenceFilter
    , ProximateAnalysisFilter, ProximateAnalysisItemFilter
    , SourceAttributeFilter, SourceEntityFilter, SourceReferenceFilter
    , TaxonomicUnitsFilter, ViewProximateAnalysisTableFilter)
from .forms import (AttributeRelationForm, ChoiceSetOptionRelationForm
    , EntityRelationForm, FoodItemForm, MasterEntityForm
    , MasterAttributeForm, MasterAttributeChoicesetOptionForm
    , MasterChoiceSetOptionForm, MasterReferenceForm
    , ProximateAnalysisForm, ProximateAnalysisItemForm
    , SourceAttributeForm, SourceAttributeChoicesetOptionForm
    , SourceChoiceSetOptionForm, SourceChoiceSetOptionValueForm, SourceEntityForm
    , SourceEntityRelationForm, SourceMeasurementValueForm
    , SourceReferenceAttributeForm, SourceReferenceForm
    , TaxonomicUnitsForm)
from .models import (AttributeRelation, ChoiceSetOptionRelation, DietSet
    , DietSetItem, FoodItem, EntityRelation
    , MasterAttribute, MasterChoiceSetOption, MasterEntity, MasterReference
    , ProximateAnalysis, ProximateAnalysisItem
    , RelationClass
    , SourceAttribute, SourceChoiceSetOption, SourceChoiceSetOptionValue, SourceEntity
    , SourceMeasurementValue, SourceReference, ViewMasterTraitValue, ViewProximateAnalysisTable)
from itis.models import TaxonomicUnits
import requests
# Begin imports for matplotlib
import io
import matplotlib.pyplot as plt
import urllib, base64
import mpltern
from mpltern.ternary.datasets import get_scatter_points
import numpy as np
# end


def index(request):
    return render(request, 'mb/index.html',)

def index_diet(request):
    num_diet_taxa=DietSet.objects.is_active().values('taxon_id').distinct().count()
    num_diet_set=DietSet.objects.is_active().count()
    num_diet_set_item=DietSetItem.objects.is_active().count()
    num_food_item=DietSetItem.objects.is_active().values('food_item_id').distinct().count()

    return render(request, 'mb/index_diet.html', context={'num_diet_taxa':num_diet_taxa, 'num_diet_set':num_diet_set, 'num_diet_set_item':num_diet_set_item, 'num_food_item':num_food_item},)

def index_mammals(request):
    return render(request, 'mb/index_mammals.html',)

def index_news(request):
    return render(request, 'mb/index_news.html',)

def index_proximate_analysis(request):
    return render(request, 'mb/index_proximate_analysis.html',)

class attribute_relation_delete(DeleteView):
    model = AttributeRelation
    def get_success_url(self):
        attribute_relation = super(attribute_relation_delete, self).get_object()
        sa_id = attribute_relation.source_attribute.id
        return reverse_lazy(
            'source_attribute-detail',
            args=(sa_id,)
        )

def attribute_relation_detail(request, pk):
    attribute_relation = get_object_or_404(AttributeRelation, pk=pk)
    return render(request, 'mb/attribute_relation_detail.html', {'attribute_relation': attribute_relation})

def attribute_relation_edit(request, pk):
    attribute_relation = get_object_or_404(AttributeRelation, pk=pk)
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

class choiceset_option_relation_delete(DeleteView):
    model = ChoiceSetOptionRelation
    def get_success_url(self):
        choiceset_option_relation = super(choiceset_option_relation_delete, self).get_object()
        sco_id = choiceset_option_relation.source_choiceset_option.id
        return reverse_lazy(
            'source_choiceset_option-detail',
            args=(sco_id,)
        )

def choiceset_option_relation_detail(request, pk):
    choiceset_option_relation = get_object_or_404(ChoiceSetOptionRelation, pk=pk)
    return render(request, 'mb/choiceset_option_relation_detail.html', {'choiceset_option_relation': choiceset_option_relation})

def choiceset_option_relation_edit(request, pk):
    choiceset_option_relation = get_object_or_404(ChoiceSetOptionRelation, pk=pk)
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

def diet_set_detail(request, pk):
    diet_set = get_object_or_404(DietSet, pk=pk)
    return render(request, 'mb/diet_set_detail.html', {'ds': diet_set})

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
    diet_set_item = get_object_or_404(DietSetItem, pk=pk)

    if diet_set_item.food_item.tsn is None:
        tsn_id = -1
        hierarchy = ''
        hierarchy_string = ''
        common_names = ''
    else:
        tsn_id = diet_set_item.food_item.tsn.tsn
        taxonomic_unit = get_object_or_404(TaxonomicUnits, tsn=tsn_id)

        response1 = requests.get("https://www.itis.gov/ITISWebService/jsonservice/getCommonNamesFromTSN?tsn="+str(tsn_id))
        r1 = response1.json()
        response2 = requests.get("https://www.itis.gov/ITISWebService/jsonservice/getFullHierarchyFromTSN?tsn="+str(tsn_id))
        r2 = response2.json()

        strings1 = []
        strings2 = []
        strings3 = []

        i=0
        while r2['hierarchyList']:
            strings1.append(r2['hierarchyList'][i]['tsn'])
            strings2.append(r2['hierarchyList'][i]['taxonName'])
            if r2['hierarchyList'][i]['tsn'] == str(tsn_id):
                break
            i += 1

        if str(r1['commonNames'][0]) != 'None':
            j=0
            while j < len(r1['commonNames']):
                strings3.append(r1['commonNames'][j]['commonName'])
                j += 1
            common_names = ', '.join(strings3)
        else:
            common_names = ''

        hierarchy_string = '-'.join(strings1)
        hierarchy = '-'.join(strings2)
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
class entity_relation_delete(DeleteView):
    model = EntityRelation
    def get_success_url(self):
        entity_relation = super(entity_relation_delete, self).get_object()
        se_id = entity_relation.source_entity.id
        return reverse_lazy(
            'source_entity-detail',
            args=(se_id,)
        )

def entity_relation_detail(request, pk):
    entity_relation = get_object_or_404(EntityRelation, pk=pk)
    return render(request, 'mb/entity_relation_detail.html', {'entity_relation': entity_relation})

def entity_relation_edit(request, pk):
    entity_relation = get_object_or_404(EntityRelation, pk=pk)
    if request.method == "POST":
        form = EntityRelationForm(request.POST, instance=entity_relation)
        if form.is_valid():
            entity_relation = form.save(commit=False)
            entity_relation.save()
            return redirect('entity_relation-detail', pk=entity_relation.pk)
    else:
        form = EntityRelationForm(instance=entity_relation)
    return render(request, 'mb/entity_relation_edit.html', {'form': form})

class food_item_delete(DeleteView):
    model = FoodItem
    success_url = reverse_lazy('food_item-list')

def food_item_detail(request, pk):
    food_item = get_object_or_404(FoodItem, pk=pk)
    if food_item.tsn.hierarchy_string:
        tsn_hierarchy = food_item.tsn.hierarchy_string.split("-")
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
    return render(request, 'mb/food_item_detail.html', {'proximate_analysis': proximate_analysis, 'food_item': food_item, })

def food_item_edit(request, pk):
    food_item = get_object_or_404(FoodItem, pk=pk)
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

class master_attribute_delete(DeleteView):
    model = MasterAttribute
    def get_success_url(self):
        master_attribute = super(master_attribute_delete, self).get_object()
        mr_id = master_attribute.reference.id
        return reverse_lazy(
            'master_reference-detail',
            args=(mr_id,)
        )

def master_attribute_detail(request, pk):
    master_attribute = get_object_or_404(MasterAttribute, pk=pk)
    return render(request, 'mb/master_attribute_detail.html', {'master_attribute': master_attribute})

def master_attribute_edit(request, pk):
    master_attribute = get_object_or_404(MasterAttribute, pk=pk)
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

    return render(
        request,
        'mb/master_attribute_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

@login_required
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

class master_choiceset_option_delete(DeleteView):
    model = MasterChoiceSetOption
    def get_success_url(self):
        obj = super(master_choiceset_option_delete, self).get_object()
        ma_id = obj.master_attribute.id
        return reverse_lazy(
            'master_attribute-detail',
            args=(ma_id,)
        )

def master_choiceset_option_detail(request, pk):
    master_choiceset_option = get_object_or_404(MasterChoiceSetOption, pk=pk)
    return render(request, 'mb/master_choiceset_option_detail.html', {'master_choiceset_option': master_choiceset_option})

@login_required
def master_choiceset_option_edit(request, pk):
    master_choiceset_option = get_object_or_404(MasterChoiceSetOption, pk=pk)
    if request.method == "POST":
        form = MasterChoiceSetOptionForm(request.POST, instance=master_choiceset_option)
        if form.is_valid():
            master_choiceset_option = form.save(commit=False)
            master_choiceset_option.save()
            return redirect('master_choiceset_option-detail', pk=master_choiceset_option.pk)
    else:
        form = MasterChoiceSetOptionForm(instance=master_choiceset_option)
    return render(request, 'mb/master_choiceset_option_edit.html', {'form': form})

class master_entity_delete(DeleteView):
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
    master_entity = get_object_or_404(MasterEntity, pk=pk)
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
            select se.name saurce_taxon
                , ma.id master_attribute_id
                , ma.name master_attribute
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

# https://medium.com/@mdhv.kothari99/matplotlib-into-django-template-5def2e159997
# https://mpltern.readthedocs.io/en/latest/index.html
    ax = plt.subplot(projection='ternary')
    if ternary:
        cf_ash = ternary[0]['cf']+ternary[0]['ash']
        nfe = ternary[0]['nfe']
        cp_ee = ternary[0]['cp']+ternary[0]['ee']
    else:
        cf_ash = 1.0
        nfe = 0.0
        cp_ee = 0.0

    ax.scatter(cf_ash, nfe, cp_ee)

# Animalivory
    t = [0.0, 0.0, 0.1, 0.2, 0.2]
    l = [0.0, 0.3, 0.3, 0.2, 0.0]
    r = [1.0, 0.7, 0.6, 0.6, 0.8]
    ax.fill(t, l, r, alpha=0.2, color='blue')
    ax.text(0.2, 0.1, 0.7, 'Animalivores', ha='center', va='center')

# Herbivory
    t = [0.3, 0.5, 0.5, 0.4]
    l = [0.5, 0.5, 0.4, 0.4]
    r = [0.2, 0.0, 0.1, 0.2]
    ax.fill(t, l, r, alpha=0.2, color='green')
    ax.text(0.5, 0.4, 0.1, 'Herbivores', ha='center', va='center')

# Frugivory
    t = [0.0, 0.0, 0.3, 0.3, 0.2]
    l = [0.7, 1.0, 0.7, 0.5, 0.5]
    r = [0.3, 0.0, 0.0, 0.2, 0.3]
    ax.fill(t, l, r, alpha=0.2, color='pink')
    ax.text(0.3, 0.6, 0.1, 'Frugivores', ha='center', va='center')

# Omnivory
    t = [0.0, 0.0, 0.3, 0.3, 0.2]
    l = [0.4, 0.65, 0.35, 0.2, 0.2]
    r = [0.6, 0.35, 0.35, 0.5, 0.6]
    ax.fill(t, l, r, alpha=0.2, color='red')
    ax.text(0.3, 0.25, 0.45, 'Omnivores', ha='center', va='center')

    ax.grid()
    ax.legend()
    ax.set_tlabel('CF + ASH')
    ax.set_llabel('NFE')
    ax.set_rlabel('CP + EE')

#    plt.plot([1, 2, 3, 4], [1, 4, 2, 3])  # Matplotlib plot.
    fig = plt.gcf() # gcf - get current figure

    # convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    fig.clf()   # clear the fig
# End Ternary plot data

    return render(request, 'mb/master_entity_detail.html', {'master_entity': master_entity, 'measurements': measurements, 'diets': diets, 'ternary':ternary, 'data':uri,})


def master_entity_edit(request, pk):
    master_entity = get_object_or_404(MasterEntity, pk=pk)
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
    f = MasterEntityFilter(request.GET, queryset=MasterEntity.objects.is_active().filter(reference_id=4).order_by('name'))

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

class master_reference_delete(DeleteView):
    model = MasterReference
    success_url = reverse_lazy('master_reference-list')

def master_reference_detail(request, pk):
    master_reference = get_object_or_404(MasterReference, pk=pk)
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

def master_reference_edit(request, pk):
    master_reference = get_object_or_404(MasterReference, pk=pk)
    if request.method == "POST":
        form = MasterReferenceForm(request.POST, instance=master_reference)
        if form.is_valid():
            master_reference = form.save(commit=False)
            master_reference.save()
            return redirect('master_reference-detail', pk=master_reference.pk)
    else:
        form = MasterReferenceForm(instance=master_reference)
    return render(request, 'mb/master_reference_edit.html', {'form': form})

def master_reference_list(request):
    f = MasterReferenceFilter(request.GET, queryset=MasterReference.objects.is_active())

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
        'mb/master_reference_list.html',
        {'page_obj': page_obj, 'filter': f,}
    )

class proximate_analysis_delete(DeleteView):
    model = ProximateAnalysis
    success_url = reverse_lazy('proximate_analysis-list')

def proximate_analysis_detail(request, pk):
    proximate_analysis = get_object_or_404(ProximateAnalysis, pk=pk)
    return render(request, 'mb/proximate_analysis_detail.html', {'proximate_analysis': proximate_analysis})

def proximate_analysis_edit(request, pk):
    proximate_analysis = get_object_or_404(ProximateAnalysis, pk=pk)
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

class proximate_analysis_item_delete(DeleteView):
    model = ProximateAnalysisItem
    success_url = reverse_lazy('proximate_analysis_item-list')

def proximate_analysis_item_detail(request, pk):
    proximate_analysis_item = get_object_or_404(ProximateAnalysisItem, pk=pk)
    return render(request, 'mb/proximate_analysis_item_detail.html', {'proximate_analysis_item': proximate_analysis_item})

def proximate_analysis_item_edit(request, pk):
    proximate_analysis_item = get_object_or_404(ProximateAnalysisItem, pk=pk)
    if request.method == "POST":
        form = ProximateAnalysisItemForm(request.POST, instance=proximate_analysis_item)
        if form.is_valid():
            proximate_analysis_item = form.save(commit=False)
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
    master_reference = get_object_or_404(MasterReference, pk=pk)

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

class source_attribute_delete(DeleteView):
    model = SourceAttribute
    def get_success_url(self):
        source_attribute = super(source_attribute_delete, self).get_object()
        sr_id = source_attribute.reference.id
        return reverse_lazy(
            'source_reference-detail',
            args=(sr_id,)
        )

def source_attribute_detail(request, pk):
    source_attribute = get_object_or_404(SourceAttribute, pk=pk)
    return render(request, 'mb/source_attribute_detail.html', {'source_attribute': source_attribute})

def source_attribute_edit(request, pk):
    source_attribute = get_object_or_404(SourceAttribute, pk=pk)
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

class source_choiceset_option_delete(DeleteView):
    model = SourceChoiceSetOption
    def get_success_url(self):
        obj = super(source_choiceset_option_delete, self).get_object()
        sa_id = obj.source_attribute.id
        return reverse_lazy(
            'source_attribute-detail',
            args=(sa_id,)
        )

def source_choiceset_option_detail(request, pk):
    source_choiceset_option = get_object_or_404(SourceChoiceSetOption, pk=pk)
    return render(request, 'mb/source_choiceset_option_detail.html', {'source_choiceset_option': source_choiceset_option})

@login_required
def source_choiceset_option_edit(request, pk):
    source_choiceset_option = get_object_or_404(SourceChoiceSetOption, pk=pk)
    if request.method == "POST":
        form = SourceChoiceSetOptionForm(request.POST, instance=source_choiceset_option)
        if form.is_valid():
            source_choiceset_option = form.save(commit=False)
            source_choiceset_option.save()
            return redirect('source_choiceset_option-detail', pk=source_choiceset_option.pk)
    else:
        form = SourceChoiceSetOptionForm(instance=source_choiceset_option)
    return render(request, 'mb/source_choiceset_option_edit.html', {'form': form})

class source_choiceset_option_value_delete(DeleteView):
    model = SourceChoiceSetOptionValue
    def get_success_url(self):
        obj = super(source_choiceset_option_value_delete, self).get_object()
        source_entity_id = obj.source_entity.id
        return reverse_lazy(
            'source_entity-detail',
            args=(source_entity_id,)
        )

def source_choiceset_option_value_detail(request, pk):
    source_choiceset_option_value = get_object_or_404(SourceChoiceSetOptionValue, pk=pk)
    return render(request, 'mb/source_choiceset_option_value_detail.html', {'source_choiceset_option_value': source_choiceset_option_value})

def source_choiceset_option_value_edit(request, pk):
    source_choiceset_option_value = get_object_or_404(SourceChoiceSetOptionValue, pk=pk)
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

class source_entity_delete(DeleteView):
    model = SourceEntity
    success_url = reverse_lazy('source_entity-list')

def source_entity_detail(request, pk):
    source_entity = get_object_or_404(SourceEntity, pk=pk)
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

def source_entity_edit(request, pk):
    source_entity = get_object_or_404(SourceEntity, pk=pk)
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

class source_measurement_value__delete(DeleteView):
    model = SourceMeasurementValue
    def get_success_url(self):
        obj = super(source_measurement_value__delete, self).get_object()
        source_entity_id = obj.source_entity.id
        return reverse_lazy(
            'source_entity-detail',
            args=(source_entity_id,)
        )

def source_measurement_value_detail(request, pk):
    source_measurement_value = get_object_or_404(SourceMeasurementValue, pk=pk)
    return render(request, 'mb/source_measurement_value_detail.html', {'source_measurement_value': source_measurement_value})

def source_measurement_value_edit(request, pk):
    source_measurement_value = get_object_or_404(SourceMeasurementValue, pk=pk)
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

class source_reference_delete(DeleteView):
    model = SourceReference
    success_url = reverse_lazy('source_reference-list')

@login_required
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
def source_reference_attribute_new(request, source_reference):
    reference = get_object_or_404(SourceReference, pk=source_reference, is_active=1)
    if request.method == "POST":
        form = SourceReferenceAttributeForm(request.POST)
        if form.is_valid():
            source_attribute = form.save(commit=False)
            source_attribute.reference = reference
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
        , 'sr_entities': sr_entities
        ,})

def source_reference_edit(request, pk):
    source_reference = get_object_or_404(SourceReference, pk=pk)
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

class tsn_delete(DeleteView):
    model = TaxonomicUnits
    success_url = reverse_lazy('tsn-list')

def tsn_detail(request, tsn):
    tsn = get_object_or_404(TaxonomicUnits, tsn=tsn)
    tsn_hierarchy = tsn.hierarchy_string.split("-")
    i=len(tsn_hierarchy)-1
    found=False
    while(i>=0 and found is False):
        pa=ViewProximateAnalysisTable.objects.filter(tsn__hierarchy_string__endswith=tsn_hierarchy[i])
        if len(pa)>=1:
            break
        i=i-1

    return render(request, 'mb/tsn_detail.html', {'pa': pa, 'tsn': tsn},)

def tsn_edit(request, tsn):
    tsn = get_object_or_404(TaxonomicUnits, tsn=tsn)
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
