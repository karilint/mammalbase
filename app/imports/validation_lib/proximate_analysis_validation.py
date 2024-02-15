from .base_validation import Validation


class Proximate_analysis_validation(Validation):

    def __init__(self):
        super().__init__()

        self.rules = {
            "verbatimScientificName"                    : "required|alpha",                                     #Done
            "PartOfOrganism"                            : "required|in:BARK,BLOOD,BONES,BUD,CARRION,EGGS,EXUDATES,FECES,FLOWER,FRUIT,LARVAE,LEAF,MINERAL,NECTAR/JUICE,NONE,POLLEN,ROOT,SEED,SHOOT,STEM,UNKNOWN,WHOLE",  #Done
            "author"                                    : "required|author",                                    #Done
            "references"                                : "required|min:10|max:500|regex:.*([1-2][0-9]{3})",    #Done
            "individualCount"                           : "digits", 
            "measurementMethod"                         : "max:500",
            "measurementDeterminedBy"                   : "",
            "verbatimLocality"                          : "max:250",   #Done
            "measurementRemarks"                        : "",
            "verbatimEventDate"                         : "max:250",   #Done
            "verbatimTraitValue__moisture"              : "max:250",   #Done
            "dispersion__moisture"                      : "",
            "measurementMethod__moisture"               : "",
            "verbatimTraitValue__dry_matter"            : "max:250",   #Done
            "dispersion__dry_matter"                    : "",
            "measurementMethod__dry_matter"             : "",
            "verbatimTraitValue__ether_extract"         : "max:250",   #Done
            "dispersion__ether_extract"                 : "",
            "measurementMethod__ether_extract"          : "",
            "verbatimTraitValue__crude_protein"         : "max:250",   #Done
            "dispersion__crude_protein"                 : "",
            "measurementMethod__crude_protein"          : "",
            "verbatimTraitValue__crude_fibre"           : "max:250",   #Done
            "dispersion__crude_fibre"                   : "",
            "measurementMethod__crude_fibre"            : "",
            "verbatimTraitValue_ash"                    : "max:250",   #Done
            "dispersion__ash"                           : "",
            "measurementMethod_ash"                     : "",
            "verbatimTraitValue__nitrogen_free_extract" : "max:250",   #Done
            "dispersion__nitrogen_free_extract"         : "",
            "measurementMethod__nitrogen_free_extract"  : "",
            "associatedReferences"                      : "max:500|regex:.*([1-2][0-9]{3}"
        }
    
        self.data = {
            "verbatimScientificName": "",
            "PartOfOrganism": "",
            "author": "",
            "references"
            "individualCount": "",
            "measurementMethod": "",
            "measurementDeterminedBy": "",
            "verbatimLocality": "",
            "measurementRemarks": "",
            "verbatimEventDate": "",
            "verbatimTraitValue__moisture": "",
            "dispersion__moisture": "",
            "measurementMethod__moisture": "",
            "verbatimTraitValue__dry_matter": "",
            "dispersion__dry_matter": "",
            "measurementMethod__dry_matter": "",
            "verbatimTraitValue__ether_extract": "",
            "dispersion__ether_extract": "",
            "measurementMethod__ether_extract": "",
            "verbatimTraitValue__crude_protein": "",
            "dispersion__crude_protein": "",
            "measurementMethod__crude_protein": "",
            "verbatimTraitValue__crude_fibre": "",
            "dispersion__crude_fibre": "",
            "measurementMethod__crude_fibre": "",
            "verbatimTraitValue_ash": "",
            "dispersion__ash": "",
            "measurementMethod_ash": "",
            "verbatimTraitValue__nitrogen_free_extract": "",
            "dispersion__nitrogen_free_extract": "",
            "measurementMethod__nitrogen_free_extract": "",
            "associatedReferences": ""
            }