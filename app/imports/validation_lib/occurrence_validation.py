
class Occurrence_validation():
    rules = {
        "references": "required | min:10 | max:500| regex:.*([1-2][0-9]{3}) | in_db:SourceReference,citation__iexact", #DONE
        "verbatimScientificName": "required",
        "scientificNameAuthorship": "",
        "taxonRank": "in:subspecies, varietas, forma, species, genus, nothogenus, nothospecies,  nothosubspecies, family", #DONE
        "organismQuantity": "digits", #DONE
        "organismQuantityType": "",
        "sex": "in:male,female,None", #DONE
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
        "author": "required | author", #DONE
        "associatedReferences": "",
        "samplingProtocol": "",
        "habitatType": "",
        "habitatPercentage": ""
    }



    # diet set
    # BARK, BLOOD, BONES, BUD, CARRION, EGGS, EXUDATES, FECES, FLOWER, FRUIT, LARVAE, LEAF, MINERAL, NECTAR/JUICE, NONE, POLLEN, ROOT, SEED, SHOOT, STEM, UNKNOWN, WHOLE