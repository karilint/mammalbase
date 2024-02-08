
class Occurrence_validation():
    rules = {
        "references": "required | min:10 | max:500| regex:.*([1-2][0-9]{3}) | in_db:SourceReference,citation__iexact", #DONE
        "verbatimScientificName": "required | alpha", #Done
        "scientificNameAuthorship": "nameYear", #Done
        "taxonRank": "in:subspecies, varietas, forma, species, genus, nothogenus, nothospecies,  nothosubspecies, family", #DONE
        "organismQuantity": "digits", #DONE
        "organismQuantityType": "", #DONE, no possible validator since darvincore quote "whereas this term allows for any string literal value." e.g '% biomass'
        "sex": "in:male,female,None", #DONE
        "lifeStage": "alpha", #Only accept alphabeticals
        "verbatimEventDate": "in: I,V,X,L,C,D,M,1,2,3,4,5,6,7,8,9", #DONE
        "occurrenceRemarks": "", #DONE, cannot be tested since it can be anything
        "verbatimLocality": "", #DONE, cannot be tested since it can be anything
        "verbatimElevation": "in:0,1,2,3,4,5,6,7,8,9", #DONE
        "verbatimDepth": "in:0,1,2,3,4,5,6,7,8,9", #DONE
        "verbatimCoordinates": "in:N,E,S,W,°,T,d", #DONE
        "verbatimLatitude": "in:N,E,S,W,°,T,d", #DONE
        "verbatimLongitude": "in:N,E,S,W,°,T,d", #DONE
        "verbatimCoordinateSystem": "in:decimal degrees,degrees decimal minutes, degrees decimal seconds, UTM ", #Done
        "verbatimSRS": "", #Maybe done maybe kesken
        "author": "required | author", #DONE
        "associatedReferences": "", #DONE, can be anything
        "samplingProtocol": "", #DONE, no possible validator since darincore quote "whereas this term allows for any string literal value." e.g 'Takats et al. 2001. Guidelines for Nocturnal Owl Monitoring in North America. Beaverhill Bird Observatory and Bird Studies Canada, Edmonton, Alberta. 32 pp., http://www.bsc-eoc.org/download/Owl.pdf'
        "habitatType": "", #DONE, no possible validator since darincore quote "whereas this term allows for any string literal value." e.g 'B (bushland): densely growing woody vegetation of shrubby habit, low stature <6 m in height, canopy cover >20%'
        "habitatPercentage": "digit"
    }



    # diet set
    # BARK, BLOOD, BONES, BUD, CARRION, EGGS, EXUDATES, FECES, FLOWER, FRUIT, LARVAE, LEAF, MINERAL, NECTAR/JUICE, NONE, POLLEN, ROOT, SEED, SHOOT, STEM, UNKNOWN, WHOLE