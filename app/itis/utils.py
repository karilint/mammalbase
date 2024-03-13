import itis.views as itis

def create_return_data(self, tsn, scientific_name, status='valid'):
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