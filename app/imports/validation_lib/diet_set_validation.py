from .base_validation import Validation


class Diet_set_validation(Validation):

    def __init__(self):
        """
        Rules for diet set validation.
        """
        super().__init__()

        self.rules = {
            "author":                       "required|author", 
            "verbatimScientificName":       "required|alpha", 
            "taxonRank":                    "in:Subspecies,Varietas,Forma,Species,Genus,Nothogenus,Nothospecies,Nothosubspecies,Family,nan", 
            "verbatimLocality":             "max:250", 
            "habitat" :                     "max:250", 
            "samplingEffort" :              "max:250",
            "sex":                          "in:male,female,nan", 
            "individualCount" :             "digits",
            "verbatimEventDate":            "max:250", 
            "measurementMethod " :          "max:500", 
            "verbatimAssociatedTaxa" :      "max:250", 
            "PartOfOrganism" :              "in:BARK,BLOOD,BONES,BUD,CARRION,EGGS,EXUDATES,FECES,FLOWER,FRUIT,LARVAE,LEAF,MINERAL,NECTAR/JUICE,NONE,POLLEN,ROOT,SEED,SHOOT,STEM,UNKNOWN,WHOLE",
            "sequence" :                    "max:250", 
            "measurementValue" :            "digis|min:0", 
            "associatedReferences" :        "max:250", 
            "references":                   "required|min:10|max:500|regex:.*([1-2][0-9]{3})", 
        }

    
        self.data = {
            "author": "",
            "verbatimScientificName": "",
            "taxonRank": "",
            "verbatimLocality": "",
            "habitat": "",
            "samplingEffort": "",
            "sex": "",
            "individualCount": "",
            "verbatimEventDate": "",
            "measurementMethod": "",
            "verbatimAssociatedTaxa": "",
            "PartOfOrganism": "",
            "sequence": "",
            "measurementValue": "",
            "associatedReferences": "",
            "references": ""
        }
    

