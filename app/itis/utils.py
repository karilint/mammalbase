import itis.views as itis
from itis.models import TaxonomicUnits
from itis.views import *
from itis.models import TaxonomicUnits, Kingdom, TaxonUnitTypes

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