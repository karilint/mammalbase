import re
import json
import sys
import traceback
from datetime import timedelta
from decimal import Decimal

import requests

import pandas as pd
import numpy

from django.contrib import messages
from django.db import transaction
from django.db import DatabaseError
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from requests_cache import CachedSession

from mb.models.models import ChoiceValue, DietSet, EntityClass, MasterReference, SourceAttribute, SourceChoiceSetOptionValue
from mb.models.models import SourceChoiceSetOption, SourceEntity, SourceMeasurementValue, SourceMethod
from mb.models.location_models import SourceLocation
from mb.models.models import SourceReference, SourceStatistic, SourceUnit, TimePeriod, DietSetItem, FoodItem ,EntityRelation
from mb.models.models import MasterEntity, ProximateAnalysisItem, ProximateAnalysis
from mb.models.occurrence_models import *
from itis.models import TaxonomicUnits, Kingdom, TaxonUnitTypes
import itis.views as itis
from config.settings import ITIS_CACHE

def make_harvard_citation_journalarticle(title, d, authors, year, container_title, volume, issue, page):
    citation = ""
    for a in authors:
        if authors.index(a) == len(authors) - 1:
            citation += str(a)
        else:
            citation += str(a) + ", "
    
    citation += " " + str(year) + ". " + str(title) + ". " + str(container_title) + ". " + str(volume) + "(" + str(issue) + "), pp." + str(page) + ". Available at: " + str(d) + "." 
    return citation

def create_return_data(tsn, scientific_name, status='valid'):
    hierarchy = None
    classification_path = ""
    classification_path_ids = ""
    classification_path_ranks = ""
    if status in {'valid', 'accepted'}:
        hierarchy = itis.getFullHierarchyFromTSN(tsn)
        classification_path = itis.hierarchyToString(scientific_name, hierarchy, 'hierarchyList', 'taxonName')
        classification_path_ids = itis.hierarchyToString(tsn, hierarchy, 'hierarchyList', 'tsn', stop_index=classification_path.count("-"))
        classification_path_ranks = itis.hierarchyToString('Species', hierarchy, 'hierarchyList', 'rankName', stop_index=classification_path.count("-"))
    return_data = {
        'taxon_id': tsn,
        'canonical_form': scientific_name,
        'classification_path_ids': classification_path_ids,
        'classification_path': classification_path,
        'classification_path_ranks': classification_path_ranks,
        'taxonomic_status':status
    }
    return {'data': [{'results': [return_data]}]}

def get_accepted_tsn(tsn):
    response = itis.GetAcceptedNamesfromTSN(tsn)
    accepted_tsn = response["acceptedNames"][0]["acceptedTsn"]
    scientific_name = response["acceptedNames"][0]["acceptedName"]
    return_data = create_return_data(accepted_tsn, scientific_name)
    
    return return_data

def create_tsn(results, tsn):
    taxonomic_unit = TaxonomicUnits.objects.filter(tsn=tsn)
    if len(taxonomic_unit)==0:
        completename = results['data'][0]['results'][0]['canonical_form']
        hierarchy_string = results['data'][0]['results'][0]['classification_path_ids']
        hierarchy = results['data'][0]['results'][0]['classification_path']
        kingdom_id = 0
        rank = 0
        
        if len(hierarchy)>0:
            kingdom = hierarchy.replace('|', '-').split('-')[0]
            kingdom_id = Kingdom.objects.filter(name=kingdom)[0].pk
            path_rank = results['data'][0]['results'][0]['classification_path_ranks'].replace('|', '-').split('-')[-1]
            rank = TaxonUnitTypes.objects.filter(rank_name=path_rank, kingdom_id=kingdom_id)[0].pk
        
        taxonomic_unit = TaxonomicUnits(tsn=tsn, kingdom_id=kingdom_id, rank_id=rank, completename=completename, hierarchy_string=hierarchy_string, hierarchy=hierarchy, common_names=None, tsn_update_date=None)
        print(taxonomic_unit)
        taxonomic_unit.save()
    else:
        taxonomic_unit = taxonomic_unit[0]

    if results['data'][0]['results'][0]['taxonomic_status'] in ("invalid", "not accepted"):
        accepted_results = get_accepted_tsn(tsn)
        accepted_taxonomic_unit = create_tsn(accepted_results, int(accepted_results['data'][0]['results'][0]['taxon_id']))
        sl_qs = itis.SynonymLinks.objects.all().filter(tsn = tsn)
        if len(sl_qs) == 0:
            sl = itis.SynonymLinks(tsn = taxonomic_unit, tsn_accepted = accepted_taxonomic_unit, tsn_accepted_name = accepted_taxonomic_unit.completename)
            print(sl)
            sl.save()
        else:
            sl = sl_qs[0]
        taxonomic_unit.hierarchy_string = accepted_taxonomic_unit.hierarchy_string
        taxonomic_unit.hierarchy = accepted_taxonomic_unit.hierarchy
        taxonomic_unit.kingdom_id = accepted_taxonomic_unit.kingdom_id
        taxonomic_unit.rank_id = accepted_taxonomic_unit.rank_id
        print(taxonomic_unit)
        taxonomic_unit.save()

    return taxonomic_unit

def generate_rank_id(food):
    associated_taxa = re.sub(r'\W+', ' ', food).split(' ')
    for item in associated_taxa:
        if len(item) < 3:
            associated_taxa.remove(item)
    
    rank_id = {}
    head = 0
    tail = 0
    while True:
        if head == tail:
            query = associated_taxa[tail]
            head += 1
        else:
            query = associated_taxa[tail] + " " +associated_taxa[head]
            tail += 1
        results = get_fooditem_json(query)
        if len(results['data'][0]) > 0:
            rank = int(itis.getTaxonomicRankNameFromTSN(results['data'][0]['results'][0]['taxon_id'])['rankId'])
            rank_id[rank] = results
            break
        if head >= len(associated_taxa):
            break
    return rank_id

def possible_nan_to_zero(size):
    if size != size or size == 'nan':
        return 0
    return size

def possible_nan_to_none(possible):
    if possible != possible or possible == 'nan':
        return None
    return possible

def trim(text:str):
    return " ".join(text.split())

def trim_df(df):
    headers = df.columns
    for i, row in df.iterrows():
        for header in headers:
            df.at[i, header] = trim(str(df.at[i, header]))

def title_matches_citation(title, source_citation):
    # https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
    title_without_html = re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', '', title)
    title_without_space = re.sub(r'\s+', '', title_without_html)
    source_citation_without_html = re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', '', source_citation)
    source_citation_without_space = re.sub(r'\s+', '', source_citation_without_html)

    if title_without_space.lower() not in source_citation_without_space.lower():
        return False
    return True

@transaction.atomic
def create_proximate_analysis(row, df):
    headers = list(df.columns.values)
    author = get_author(getattr(row, 'author'))
    attribute_dict = {
        "reference" : get_sourcereference_citation(getattr(row, 'references'), author),
        "method" : None,
        "location" : None,
        "study_time" : None,
        "cited_reference" : None
    }
    if "measurementMethod" in headers:
        attribute_dict["method"] = get_sourcemethod(getattr(row, "measurementMethod"), attribute_dict["reference"], author)
    if "verbatimLocality" in headers:
        attribute_dict["location"] = get_sourcelocation(getattr(row, "verbatimLocality"), attribute_dict["reference"], author)
    if "verbatimEventDate" in headers:
        attribute_dict["study_time"] = getattr(row, "verbatimEventDate")
    if "associatedReferences" in headers:
        attribute_dict["cited_reference"] = getattr(row, "associatedReferences")
    pa = None
    pa_old = ProximateAnalysis.objects.filter(**attribute_dict)
    if len(pa_old) > 0:
        pa = pa_old[0]
    else:
        pa = ProximateAnalysis(**attribute_dict)
        pa.save()
    create_proximate_analysis_item(row, pa, attribute_dict["location"], attribute_dict["cited_reference"], headers)

@transaction.atomic
def create_proximate_analysis_item(row, pa, location, cited_reference, headers):
    #Names of the import fields in the model.
    pa_item_dict = {
        "proximate_analysis" : pa,
        "location" : location,
        "cited_reference" : cited_reference,
        "forage" : get_fooditem(
            getattr(row, 'verbatimScientificName'),
            possible_nan_to_none(getattr(row, "PartOfOrganism"))
        )
    }
    
    #Check if pa_item already exists
    pa_item_old = ProximateAnalysisItem.objects.filter(**pa_item_dict)
    pa_item_dict = convert_empty_values_pa(row, headers, pa_item_dict)
    pa_item_dict = generate_standard_values_pa(pa_item_dict)
    if len(pa_item_old) > 0:
        pa_item_old.update(**pa_item_dict)
    else:
        pa_item = ProximateAnalysisItem(**pa_item_dict)
        pa_item.save()

def convert_empty_values_pa(row, headers, pa_item_dict):
    pa_item_dict_new = pa_item_dict

    proximate_analysis_item_headers = {
        "individualCount":{
            "name":"sample_size",
            "type":int
        },
        "measurementDeterminedBy":{
            "name":"measurement_determined_by",
            "type":str
        },
        "measurementRemarks":{
            "name":"measurement_remarks",
            "type":str
        },
        "verbatimTraitValue__moisture":{
            "name":"moisture_reported",
            "type":float
        },
        "dispersion__moisture":{
            "name":"moisture_dispersion",
            "type":float
        },
        "measurementMethod__moisture":{
            "name":"moisture_measurement_method",
            "type":str
        },
        "verbatimTraitValue__dry_matter":{
            "name":"dm_reported",
            "type":float
        },
        "dispersion__dry_matter":{
            "name":"dm_dispersion",
            "type":float
        },
        "measurementMethod__dry_matter":{
            "name":"dm_measurement_method",
            "type":str
        },
        "verbatimTraitValue__ether_extract":{
            "name":"ee_reported",
            "type":float
        },
        "dispersion__ether_extract":{
            "name":"ee_dispersion",
            "type":float
        },
        "measurementMethod__ether_extract":{
            "name":"ee_measurement_method",
            "type":str
        },
        "verbatimTraitValue__crude_protein":{
            "name":"cp_reported",
            "type":float
        },
        "dispersion__crude_protein":{
            "name":"cp_dispersion",
            "type":float
        },
        "measurementMethod__crude_protein":{
            "name":"cp_measurement_method",
            "type":str
        },
        "verbatimTraitValue__crude_fibre":{
            "name":"cf_reported",
            "type":float
        },
        "dispersion__crude_fibre":{
            "name":"cf_dispersion",
            "type":float
        },
        "measurementMethod__crude_fibre":{
            "name":"cf_measurement_method",
            "type":str
        },
        "verbatimTraitValue_ash":{
            "name":"ash_reported",
            "type":float
        },
        "dispersion__ash":{
            "name":"ash_dispersion",
            "type":float
        },
        "measurementMethod_ash":{
            "name":"ash_measurement_method",
            "type":str
        },
        "verbatimTraitValue__nitrogen_free_extract":{
            "name":"nfe_reported",
            "type":float
        },
        "dispersion__nitrogen_free_extract":{
            "name":"nfe_dispersion",
            "type":float
        },
        "measurementMethod__nitrogen_free_extract":{
            "name":"nfe_measurement_method",
            "type":str
        },
        "associatedReferences":{
            "name":"cited_reference",
            "type":str
        }
    }
    
    for header in proximate_analysis_item_headers.keys():
        if header in headers:
            value = getattr(row, header)
            value = possible_nan_to_none(value)
            pa_item_dict_new[proximate_analysis_item_headers[header]["name"]] = value

    return pa_item_dict_new

def generate_standard_values_pa(items):
    standard_items = items
    remarks_text = "CP+EE+CF+NFE+ASH = 100"
    # Sum of reported values excluding dry matter and moisture
    item_sum = Decimal(0.0)
    for item in items.keys():
        if "reported" in item and "dm" not in item and "moisture" not in item and items[item] is not None:
            item_sum += Decimal(items[item])
    
    # If reported values sum to 1000 instead of 100 then divide sum by 10
    sum_to_thousand = False
    if abs(item_sum - Decimal(100)) > abs(item_sum - Decimal(1000)):
        sum_to_thousand = True
        remarks_text = "CP+EE+CF+NFE+ASH = 1000"
        item_sum /= Decimal(10)

    # If the sum of reported values is closer to 100 when moisture is included then add moisture to the sum
    if items["moisture_reported"] is not None:
        if sum_to_thousand and abs(Decimal(100) - (item_sum + (Decimal(items["moisture_reported"]) / Decimal(10)))) < abs(Decimal(100) - item_sum):
            item_sum += Decimal(items["moisture_reported"]) / Decimal(10)
            remarks_text = "Moisture+CP+EE+CF+NFE+ASH = 1000"
        elif abs(Decimal(100) - (item_sum + Decimal(items["moisture_reported"]))) < abs(Decimal(100) - item_sum):
            item_sum += Decimal(items["moisture_reported"])
            remarks_text = "Moisture+CP+EE+CF+NFE+ASH = 100"
    elif items["dm_reported"] is not None:
        if abs(item_sum - Decimal(items["dm_reported"])) < Decimal(0.001):
            remarks_text = "CP+EE+CF+NFE+ASH = DM"
    
    for item in list(items.keys()):
        if "reported" not in item or "dm" in item or "moisture" in item:
            continue
        elif items[item] is None:
            standard_items[item.replace("reported","std")] = None
        elif sum_to_thousand:
            standard_items[item.replace("reported","std")] = ((Decimal(items[item]) / Decimal(10)) / item_sum) * Decimal(100)
        else:
            standard_items[item.replace("reported","std")] = (Decimal(items[item]) / item_sum) * Decimal(100)

    standard_items["remarks"] = remarks_text
    standard_items["transformation"] = "Original value / (CP+EE+CF+ASH+NFE) * 100"
    
    return standard_items
