from .base_validation import Validation


class Occurrence_validation(Validation):

    def __init__(self):
        """
        Rules for occurrence validation. Empty string in rules means that field do not have a validation.
        """
        super().__init__()

        self.rules = {
            "references"                : "required|min:10|max:500|regex:.*([1-2][0-9]{3})", 
            "verbatimScientificName"    : "required|alpha", 
            "taxonRank"                 : "in:Subspecies,Varietas,Forma,Species,Genus,Nothogenus,Nothospecies,Nothosubspecies,Family,nan", 
            "organismQuantity"          : "digits", 
            "sex"                       : "choiceValue:gender", 
            "lifeStage"                 : "choiceValue:lifestage", 
            "verbatimLocality"          : "max:250", 
            "verbatimElevation"         : "max:250", 
            "verbatimDepth"             : "max:250", 
            "verbatimCoordinateSystem"  : "coordinateSystem:verbatimLatitude,verbatimLongitude,verbatimCoordinates", 
            "author"                    : "required|author", 
        }
    
        self.data = {
            "references": "",
            "verbatimScientificName": "",
            "scientificNameAuthorship": "",
            "taxonRank": "",
            "organismQuantity": "",
            "organismQuantityType": "",
            "sex": "",
            "lifeStage": "",
            "verbatimEventDate": "",
            "occurrenceRemarks": "",
            "verbatimLocality": "",
            "verbatimElevation": "",
            "verbatimDepth": "",
            "verbatimCoordinates": "",
            "verbatimLatitude": "",
            "verbatimLongitude": "",
            "verbatimCoordinateSystem": "",
            "verbatimSRS": "",
            "author": "",
            "associatedReferences": "",
            "samplingProtocol": "",
            "habitatType": "",
            "habitatPercentage": ""
        }
    

