# From https://www.dataquest.io/blog/python-api-tutorial/

import requests

# Full API description can be found from https://www.gbif.org/developer/species
def match_gbif(name, **kwargs):
    name = name
    parameters = {"name": name}
    if "datasetKey" in kwargs:
        parameters['datasetKey'] = kwargs["datasetKey"]
    print(parameters)
    # Make a get request with the parameters.
    response = requests.get("https://api.gbif.org/v1/species/match", params=parameters)
    print(response.status_code)
    if response.status_code == 200:
        data = response.json()
    #    print(type(data))
    #    print(data)
        if data["status"] == 'ACCEPTED':
            print("ACCEPTED: " + data["scientificName"])
        else:
            print(data)
            if data["acceptedUsageKey"]:
                accepted = requests.get("https://api.gbif.org/v1/species/"+str(data["acceptedUsageKey"]))
                accepted_data = accepted.json()
                print(data["status"] + ": " + data["scientificName"])
                print(accepted_data["taxonomicStatus"] + ": " + accepted_data["scientificName"])
    else:
        print("NOT")

taxa = ["Artibeus hirsutus", "Artibeus hartii"
    , "Artibeus intermedius"
    , "Artibeus planirostris"
    , "Australophocaena dioptrica"
    , "Baiyankamys habbema"]

for taxon in taxa:
#    match_gbif(name = taxon, datasetKey = '672aca30-f1b5-43d3-8a2b-c1606125fa1b')
    match_gbif(name = taxon)
