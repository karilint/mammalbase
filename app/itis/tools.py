from datetime import timedelta
from requests.exceptions import ConnectionError, ReadTimeout
from requests_cache import CachedSession

from django.utils import timezone
from django.shortcuts import get_object_or_404
from config.settings import ITIS_CACHE

from .models import SynonymLinks, TaxonomicUnits

# https://www.justintodata.com/python-api-call-to-request-data/#python-example-1-yelp-api-call

def hierarchyToString(stop_word, dict, key1, key2, stop_index=-1):
    h = []
    i=0
    while dict[key1] and (stop_index==-1 or stop_index >= i):
        h.append(dict[key1][i][key2])
        if dict[key1][i][key2] == str(stop_word):
            break
        i += 1
    hierarchy_string = '-'.join(h)
    return hierarchy_string

def itis_api_call(function, params, timeout, refresh):
    search_api_url = 'https://www.itis.gov/ITISWebService/jsonservice/' + function
    session = CachedSession(ITIS_CACHE, expire_after=timedelta(days=30), stale_if_error=True)
    try:
        response = session.get(search_api_url, params=params, timeout=timeout, refresh=refresh)
    except ConnectionError:
        print('Network connection failed.')
        return None
    except ReadTimeout:
        print('timeout.')
        return None
    if response.status_code==200:
        return response.json()
    else:
        return None

def GetCommonNamesfromTSN(tsn, refresh=False):
    function = 'getCommonNamesFromTSN'
    params = {'tsn': tsn}
    return_header = 'commonNames'
    return_value = 'commonName'
    
    if int(tsn) > 0:
        data_dict = itis_api_call(function, params, 15, refresh=refresh)
        if data_dict is not None:
            return_string = ""
            if str(data_dict[return_header][0]) != 'None':
                list = []
                for i in range(0, len(data_dict[return_header])):
                    list.append(data_dict[return_header][i][return_value])
                return_string = ', '.join(list)
            return return_string
 
        else:
            return ''

def GetITISdatafromTSN(tsn, function, refresh=False):
    function = function
    params = {'tsn': tsn}

    data_dict = itis_api_call(function, params, 5, refresh=refresh)

    return data_dict

# returns dict_keys(['acceptedNames', 'class', 'tsn'])
def GetAcceptedNamesfromTSN(tsn, refresh=False):
    function = 'getAcceptedNamesFromTSN'
    params = {'tsn': tsn}

    if int(tsn) > 0:
        return itis_api_call(function, params, 15, refresh=refresh)

'''
returns dict_keys(['acceptedNameList', 'class', 'commentList', 'commonNameList', 'completenessRating', 
    'coreMetadata', 'credibilityRating', 'currencyRating', 'dateData', 'expertList', 'geographicDivisionList', 
    'hierarchyUp', 'jurisdictionalOriginList', 'kingdom','otherSourceList', 'parentTSN', 'publicationList', 
    'scientificName', 'synonymList', 'taxRank', 'taxonAuthor', 'tsn', 'unacceptReason', 'usage']
'''
def getFullHierarchyFromTSN(tsn, refresh=False):
    function = 'getFullHierarchyFromTSN'
    params = {'tsn': tsn}

    if int(tsn) > 0:
        return itis_api_call(function, params, 15, refresh=refresh)
    else:
        return None

def getFullRecordFromTSN(tsn, refresh=False):
    function = 'getFullRecordFromTSN'
    params = {'tsn': tsn}

    if int(tsn) > 0:
        return itis_api_call(function, params, 15, refresh=refresh)
    else:
        return None

# returns dict_keys(['class', 'kingdomId', 'kingdomName', 'rankId', 'rankName', 'tsn'])
def getTaxonomicRankNameFromTSN(tsn, refresh=False):
    function = 'getTaxonomicRankNameFromTSN'
    params = {'tsn': tsn}

    if int(tsn) > 0:
        return itis_api_call(function, params, 15, refresh=refresh)
    else:
        return None

# returns dict_keys(['class', 'kingdomId', 'kingdomName', 'rankId', 'rankName', 'tsn'])
def updateTSN(tsn):
    taxonomic_unit = get_object_or_404(TaxonomicUnits, tsn=tsn)
    #print(taxonomic_unit)
    itis_data = getFullRecordFromTSN(tsn, refresh=True)
    full_hierarchy = getFullHierarchyFromTSN(tsn, refresh=True)
    
    if itis_data is not None and full_hierarchy is not None:
        taxonomic_unit.kingdom_id = itis_data['taxRank']['kingdomId']
        #print(taxonomic_unit.kingdom_id)
        taxonomic_unit.rank_id = itis_data['taxRank']['rankId']
        #print(taxonomic_unit.rank_id)
        taxonomic_unit.completename = itis_data['scientificName']['combinedName']
        tsn_name = taxonomic_unit.completename
        #print(taxonomic_unit.completename)
        #print(itis_data['acceptedNameList']['acceptedNames'][0] is not None)
        if itis_data['acceptedNameList']['acceptedNames'][0] is not None:
            sl_qs = SynonymLinks.objects.all().filter(tsn = tsn)
            #print(len(sl_qs))
            if len(sl_qs) == 0:
                sl = SynonymLinks()
                sl.tsn = taxonomic_unit
            else:
                sl = sl_qs[0]
#            sl.tsn_accepted_id = itis_data['acceptedNameList']['acceptedNames'][0]['acceptedTsn']
            tsn = itis_data['acceptedNameList']['acceptedNames'][0]['acceptedTsn']
            full_hierarchy = getFullHierarchyFromTSN(tsn)
            if full_hierarchy is None:
                return False
            sl.tsn_accepted_name = itis_data['acceptedNameList']['acceptedNames'][0]['acceptedName']
            tsn_name = sl.tsn_accepted_name
#            print(sl.tsn_accepted_id)
            #print(sl.tsn_accepted_name)

            tu_accepted_qs = TaxonomicUnits.objects.all().filter(tsn = tsn)
            #print(len(tu_accepted_qs))
            if len(tu_accepted_qs) == 0:
                tu_accepted = TaxonomicUnits()
                tu_accepted.tsn = tsn
                tu_accepted.kingdom_id = 0
                tu_accepted.rank_id = 0
                tu_accepted.completename = tsn_name
                tu_accepted.save()
            else:
                tu_accepted = tu_accepted_qs[0]

            sl.tsn_accepted = tu_accepted
            sl.save()

        taxonomic_unit.common_names = ''
        if itis_data['commonNameList']['commonNames'][0] is not None:
            list = []
            for i in range(0, len(itis_data['commonNameList']['commonNames'])):
                list.append(itis_data['commonNameList']['commonNames'][i]['commonName'])
            taxonomic_unit.common_names = ', '.join(list)
            #print(taxonomic_unit.common_names)
        
        hierarchy_string = hierarchyToString(tsn, full_hierarchy, 'hierarchyList', 'tsn')
        #print(hierarchy_string)
        taxonomic_unit.hierarchy_string = hierarchy_string
        hierarchy = hierarchyToString(tsn_name, full_hierarchy, 'hierarchyList', 'taxonName')
        #print(hierarchy)
        taxonomic_unit.hierarchy = hierarchy
        taxonomic_unit.tsn_update_date = timezone.now()
        taxonomic_unit.save()
        return True
    else:
        return False

'''
        `completename` VARCHAR(200) NOT NULL,
        `common_names` VARCHAR(400) NULL DEFAULT NULL,
        `hierarchy` VARCHAR(400) NULL DEFAULT NULL,
        `hierarchy_string` VARCHAR(200) NULL DEFAULT NULL,
        `tsn_accepted` INT(11) NULL DEFAULT NULL,
        `tsn_accepted_name` VARCHAR(200) NULL DEFAULT NULL,
        `tsn_update_date` DATETIME(6) NULL DEFAULT NULL,

'''

#Used to calculate data quality score
def calculate_data_quality_score(taxon,
                                 citation,
                                 source_type,
                                 source_attribute,
                                 n_total,
                                 minimum,
                                 maximum,
                                 std,
                                 method,
                                 items):
    score = 0
    #Weight of taxon quality
    if taxon in ('Species', 'Subspecies'):
        score +=1

    #Weight of having a reported citation of the data
    if citation == 'Original study':
        score += 2
    elif citation is not None:
        score += 1

    #Weight of source quality in the diet
    if source_type == 'journal-article':
        score += 3
    elif source_type == 'book':
        score += 2
    elif source_type == 'data set':
        score += 1

    #Weight of having a described method in the method
    if source_attribute:
        score += 1

    #Weight of having individual count
    if n_total != 0:
        score += 1

    #Weight of having minimum and maximum
    if minimum != 0 and maximum != 0:
        score += 1

    #Weight of having Standard Deviation
    if std != 0:
        score += 1

    #Weight of having a described method
    if method:
        score += 2

    #Weight of the food items in the diet
    if items != "":
        if items.count():
            score += (2 * items.count()) // items.count()

    return score
