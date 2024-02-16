from .base_validation import Validation


class Occurrence_validation(Validation):

    def __init__(self):
        """
        Rules for occurrence validation.
        """
        super().__init__()

        self.rules = {
            "references"                : "required|min:10|max:500|regex:.*([1-2][0-9]{3})", #DONE #|in_db:SourceReference,citation__iexact
            "verbatimScientificName"    : "required|alpha", #Done
            "scientificNameAuthorship"  : "", #Done #nameyear ennen
            "taxonRank"                 : "in:Subspecies,Varietas,Forma,Species,Genus,Nothogenus,Nothospecies,Nothosubspecies,Family,nan", #DONE
            "organismQuantity"          : "digits", #DONE
            "organismQuantityType"      : "", #DONE, no possible validator since darvincore quote "whereas this term allows for any string literal value." e.g '% biomass'
            "sex"                       : "gender", #"in:male,female,nan", #DONE
            "lifeStage"                 : "alpha", #Only accept alphabeticals #alpha
            "verbatimEventDate"         : "", #DONE
            "occurrenceRemarks"         : "", #DONE, cannot be tested since it can be anything
            "verbatimLocality"          : "max:250", #DONE, cannot be tested since it can be anything
            "verbatimElevation"         : "max:250", #DONE
            "verbatimDepth"             : "max:250", #DONE
            "verbatimCoordinates"       : "verbatimCoordinates", #DONE
            "verbatimLatitude"          : "", #DONE
            "verbatimLongitude"         : "", #DONE
            "verbatimCoordinateSystem"  : "in:decimal degrees,degrees minutes,degrees decimal seconds,UTM,nan", #Done
            "verbatimSRS"               : "", #Maybe done maybe kesken
            "author"                    : "required|author", #DONE
            "associatedReferences"      : "", #DONE, can be anything
            "samplingProtocol"          : "", #DONE, no possible validator since darincore quote "whereas this term allows for any string literal value." e.g 'Takats et al. 2001. Guidelines for Nocturnal Owl Monitoring in North America. Beaverhill Bird Observatory and Bird Studies Canada, Edmonton, Alberta. 32 pp., http://www.bsc-eoc.org/download/Owl.pdf'
            "habitatType"               : "", #DONE, no possible validator since darincore quote "whereas this term allows for any string literal value." e.g 'B (bushland): densely growing woody vegetation of shrubby habit, low stature <6 m in height, canopy cover >20%'
            "habitatPercentage"         : "" #Done
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
    



    # diet set
    # BARK, BLOOD, BONES, BUD, CARRION, EGGS, EXUDATES, FECES, FLOWER, FRUIT, LARVAE, LEAF, MINERAL, NECTAR/JUICE, NONE, POLLEN, ROOT, SEED, SHOOT, STEM, UNKNOWN, WHOLE