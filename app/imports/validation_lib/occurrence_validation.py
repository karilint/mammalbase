from .base_validation import Validation


class Occurrence_validation(Validation):

    def __init__(self):
        """
        Rules for occurrence validation.
        """
        super().__init__()

        self.rules = {
            "references"                : "required|min:10|max:500|regex:.*([1-2][0-9]{3})", 
            "verbatimScientificName"    : "required|alpha", 
            "scientificNameAuthorship"  : "", 
            "taxonRank"                 : "in:Subspecies,Varietas,Forma,Species,Genus,Nothogenus,Nothospecies,Nothosubspecies,Family,nan", #DONE
            "organismQuantity"          : "digits", 
            "organismQuantityType"      : "", 
            "sex"                       : "gender", 
            "lifeStage"                 : "alpha", 
            "verbatimEventDate"         : "", 
            "occurrenceRemarks"         : "", 
            "verbatimLocality"          : "max:250", 
            "verbatimElevation"         : "max:250", 
            "verbatimDepth"             : "max:250", 
            "verbatimCoordinates"       : "verbatimCoordinates", 
            "verbatimLatitude"          : "", 
            "verbatimLongitude"         : "", 
            "verbatimCoordinateSystem"  : "in:decimal degrees,degrees minutes,degrees decimal seconds,UTM,nan", 
            "verbatimSRS"               : "", 
            "author"                    : "required|author", 
            "associatedReferences"      : "", 
            "samplingProtocol"          : "", 
            "habitatType"               : "", 
            "habitatPercentage"         : "max:500|regex:.*([1-2][0-9]{3}" 
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
    

