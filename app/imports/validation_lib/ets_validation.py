from .base_validation import Validation


class Ets_validation(Validation):

    def __init__(self):
        """
        Rules for ets validation.
        """
        super().__init__()

        self.rules = {
            "references": "required|min:10|max:500|regex:.*([1-2][0-9]{3})",
            "verbatimScientificName": "required|alpha",
            "taxonRank": "in:Subspecies,Varietas,Forma,Species,Genus,Nothogenus,Nothospecies,Nothosubspecies,Family,nan",
            "verbatimTraitName": "max:250",
            "verbatimTraitUnit": "max:25",
            "individualCount": "digits",
            "dispersion": "max:250",
            "statisticalMethod": "max:250",
            "verbatimTraitValue": "",
            "sex": "in:male,female,nan",
            "lifeStage": "alpha",
            "measurementMethod": "alpha",
            "measurementDeterminedBy": "",
            "verbatimLocality": "max:250",
            "author": "required|author",
            "associatedReferences": "max:500|regex:.*([1-2][0-9]{3}"
        }


    
        self.data = {
            "references": "",
            "verbatimScientificName": "",
            "taxonRank": "",
            "verbatimTraitName": "",
            "verbatimTraitUnit": "",
            "individualCount": "",
            "measurementValue_min": "",
            "measurementValue_max": "",
            "dispersion": "",
            "statisticalMethod": "",
            "verbatimTraitValue": "",
            "sex": "",
            "lifeStage": "",
            "measurementMethod": "",
            "measurementRemarks": "",
            "measurementAccuracy": "",
            "measurementDeterminedBy": "",
            "verbatimLocality": "",
            "author": "",
            "associatedReferences": ""
        }