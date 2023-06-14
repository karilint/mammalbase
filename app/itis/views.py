from django.utils import timezone

from django.shortcuts import get_object_or_404, render
import requests
from requests.exceptions import ConnectionError, ReadTimeout
from itis.models import SynonymLinks, TaxonomicUnits

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

def itis_api_call(function, params, timeout):
    search_api_url = 'https://www.itis.gov/ITISWebService/jsonservice/' + function
    try:
        response = requests.get(search_api_url, params=params, timeout=timeout)
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

def GetCommonNamesfromTSN(tsn):
    function = 'getCommonNamesFromTSN'
    params = {'tsn': tsn}
    return_header = 'commonNames'
    return_value = 'commonName'
    
    if int(tsn) > 0:
        data_dict = itis_api_call(function, params, 15)
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

def GetITISdatafromTSN(tsn, function):
    function = function
    params = {'tsn': tsn}

    data_dict = itis_api_call(function, params, 5)

    return data_dict

# returns dict_keys(['acceptedNames', 'class', 'tsn'])
def GetAcceptedNamesfromTSN(tsn):
    function = 'getAcceptedNamesFromTSN'
    params = {'tsn': tsn}

    if int(tsn) > 0:
        return itis_api_call(function, params, 15)

'''
returns dict_keys(['acceptedNameList', 'class', 'commentList', 'commonNameList', 'completenessRating', 
    'coreMetadata', 'credibilityRating', 'currencyRating', 'dateData', 'expertList', 'geographicDivisionList', 
    'hierarchyUp', 'jurisdictionalOriginList', 'kingdom','otherSourceList', 'parentTSN', 'publicationList', 
    'scientificName', 'synonymList', 'taxRank', 'taxonAuthor', 'tsn', 'unacceptReason', 'usage']
'''
def getFullHierarchyFromTSN(tsn):
    function = 'getFullHierarchyFromTSN'
    params = {'tsn': tsn}

    if int(tsn) > 0:
        return itis_api_call(function, params, 15)
    else:
        return None

def getFullRecordFromTSN(tsn):
    function = 'getFullRecordFromTSN'
    params = {'tsn': tsn}

    if int(tsn) > 0:
        return itis_api_call(function, params, 15)
    else:
        return None

# returns dict_keys(['class', 'kingdomId', 'kingdomName', 'rankId', 'rankName', 'tsn'])
def getTaxonomicRankNameFromTSN(tsn):
    function = 'getTaxonomicRankNameFromTSN'
    params = {'tsn': tsn}

    if int(tsn) > 0:
        return itis_api_call(function, params, 15)
    else:
        return None

# returns dict_keys(['class', 'kingdomId', 'kingdomName', 'rankId', 'rankName', 'tsn'])
def updateTSN(tsn):
    tsn_key = tsn
    tu = get_object_or_404(TaxonomicUnits, tsn=tsn_key)
    print(tu)
    r = getFullRecordFromTSN(tsn_key)
    if r is not None:
        tu.kingdom_id = r['taxRank']['kingdomId']
        print(tu.kingdom_id)
        tu.rank_id = r['taxRank']['rankId']
        print(tu.rank_id)
        tu.completename = r['scientificName']['combinedName']
        tsn_name = tu.completename
        print(tu.completename)
        print(r['acceptedNameList']['acceptedNames'][0] is not None)
        if r['acceptedNameList']['acceptedNames'][0] is not None:
            sl_qs = SynonymLinks.objects.all().filter(tsn = tsn_key)
            print(len(sl_qs))
            if len(sl_qs) == 0:
                sl = SynonymLinks()
                sl.tsn = tu
            else:
                sl = sl_qs[0]
#            sl.tsn_accepted_id = r['acceptedNameList']['acceptedNames'][0]['acceptedTsn']
            tsn_key = r['acceptedNameList']['acceptedNames'][0]['acceptedTsn']
            sl.tsn_accepted_name = r['acceptedNameList']['acceptedNames'][0]['acceptedName']
            tsn_name = sl.tsn_accepted_name
#            print(sl.tsn_accepted_id)
            print(sl.tsn_accepted_name)

            tu_accepted_qs = TaxonomicUnits.objects.all().filter(tsn = tsn_key)
            print(len(tu_accepted_qs))
            if len(tu_accepted_qs) == 0:
                tu_accepted = TaxonomicUnits()
                tu_accepted.tsn = tsn_key
                tu_accepted.kingdom_id = 0
                tu_accepted.rank_id = 0
                tu_accepted.completename = tsn_name
                tu_accepted.save()
            else:
                tu_accepted = tu_accepted_qs[0]

            sl.tsn_accepted = tu_accepted
            sl.save()

        tu.common_names = ''
        if r['commonNameList']['commonNames'][0] is not None:
            list = []
            j=0
            while j < len(r['commonNameList']['commonNames']):
                list.append(r['commonNameList']['commonNames'][j]['commonName'])
                j += 1
            tu.common_names = ', '.join(list)
            print(tu.common_names)

        h = getFullHierarchyFromTSN(tsn_key)
        hierarchy_string = hierarchyToString(tsn_key, h, 'hierarchyList', 'tsn')
        print(hierarchy_string)
        tu.hierarchy_string = hierarchy_string
        hierarchy = hierarchyToString(tsn_name, h, 'hierarchyList', 'taxonName')
        print(hierarchy)
        tu.hierarchy = hierarchy
        tu.tsn_update_date = timezone.now()
        tu.save()
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