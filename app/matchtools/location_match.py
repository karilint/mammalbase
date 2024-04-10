from mb.models import SourceLocation, MasterLocation, LocationRelation
from matchtools.location_api import LocationAPI

def create_master_location(geoNamesLocation: dict):
    name = geoNamesLocation["name"]
    latitude = geoNamesLocation["lat"]
    longitude = geoNamesLocation["lng"]
    location_id = geoNamesLocation["geonameId"]
    country = geoNamesLocation.get("countryName")
    country_code = geoNamesLocation.get("countryCode")
    continent = geoNamesLocation.get("continent")

    master_location = MasterLocation(name=name, decimal_latitude=latitude, decimal_longitude=longitude, location_id=location_id)
    if country:
        master_location.country = country
        master_location.country_code = country_code
    if continent:
        master_location.continent = continent

    master_location.save()
    return master_location

def match_locations(sourceLocationId, masterLocationId):
    location_relation = LocationRelation(source_location_id=sourceLocationId, master_location_id=masterLocationId)
    location_relation.save()
    return location_relation

def add_locations(geo_names_location):
    api = LocationAPI()
    hierarchy_list = api.get_location_hierarchy(geo_names_location["geonameId"])["geonames"]
    hierarchy_list = [location for location in hierarchy_list if location["name"] != geo_names_location["name"]]
    locations = [geo_names_location] + hierarchy_list
    
    continent = next((location["name"] for location in locations if location["fcode"] == "CONT"), None)

    if continent:
        for location in locations:
            if location["fcode"] != "CONT" and location["name"] != "Earth":
                location["continent"] = continent
    
    added_locations = [create_master_location(location) for location in locations]
    
    return added_locations
