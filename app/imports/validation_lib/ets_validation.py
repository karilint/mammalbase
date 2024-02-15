from .base_validation import Validation


class Ets_validation(Validation):

    def __init__(self):
        super().__init__()

        self.rules = {
            "author":                       "required|author", #DONE
            "verbatimScientificName":       "required|alpha", #Done
            "taxonRank":                    "in:Subspecies,Varietas,Forma,Species,Genus,Nothogenus,Nothospecies,Nothosubspecies,Family,nan", #DONE
            "verbatimLocality":             "max:250", #DONE, cannot be tested since it can be anything
            "habitat" :                     "max:250", # ???
            "samplingEffort" :              "max:250",
            "sex":                          "in:male,female,nan", #DONE
            "individualCount" :             "digits",
            "verbatimEventDate":            "max:250", #DONE
            "measurementMethod " :          "max:500", #max 500
            "verbatimAssociatedTaxa" :      "max:250", #DONE alkaa verbatim
            "PartOfOrganism" :              "in:BARK,BLOOD,BONES,BUD,CARRION,EGGS,EXUDATES,FECES,FLOWER,FRUIT,LARVAE,LEAF,MINERAL,NECTAR/JUICE,NONE,POLLEN,ROOT,SEED,SHOOT,STEM,UNKNOWN,WHOLE",
            "sequence" :                    "max:250", #?
            "measurementValue" :            "digis|min:0", #?
            "associatedReferences" :        "max:250", #max 250
            "references":                   "required|min:10|max:500|regex:.*([1-2][0-9]{3})", #DONE #|in_db:SourceReference,citation__iexact
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
    



    # diet set
    # BARK, BLOOD, BONES, BUD, CARRION, EGGS, EXUDATES, FECES, FLOWER, FRUIT, LARVAE, LEAF, MINERAL, NECTAR/JUICE, NONE, POLLEN, ROOT, SEED, SHOOT, STEM, UNKNOWN, WHOLE