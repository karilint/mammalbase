from mb.models import SourceLocation, MasterLocation, LocationRelation
from matchtools.location_api import LocationAPI
from django.db.models import Q

def create_master_location(geoNamesLocation: dict, prev_location: MasterLocation):
    name = geoNamesLocation["name"]
    latitude = geoNamesLocation["lat"]
    longitude = geoNamesLocation["lng"]
    location_id = geoNamesLocation["geonameId"]
    country = geoNamesLocation.get("countryName")
    country_code = geoNamesLocation.get("countryCode")
    continent = geoNamesLocation.get("continent")

    master_location, created = MasterLocation.objects.get_or_create(
        name=name, decimal_latitude=latitude, decimal_longitude=longitude, location_id=location_id
    )

    if created:
        if country:
            master_location.country = country
            master_location.country_code = country_code
            
        if continent:
            master_location.continent = continent
        
        if prev_location:
            master_location.higher_geography = prev_location

        master_location.save()
        
    return (master_location, created)

def match_locations(master_location, source_location):
    if master_location is None:
        raise ValueError("master_location cannot be None")
    
    location_relation =  LocationRelation(master_location=master_location, source_location=source_location)
    location_relation.save()
    return location_relation

def add_locations(geo_names_location, source_location_id):
    source_location = SourceLocation.objects.get(id=source_location_id)
    api = LocationAPI()
    hierarchy_list = api.get_location_hierarchy(geo_names_location["geonameId"])["geonames"]
    hierarchy_list = [location for location in hierarchy_list if location["geonameId"] != geo_names_location["geonameId"]]
    
    locations = hierarchy_list + [geo_names_location]
    continent = next((location["name"] for location in locations if location["fcode"] == "CONT"), None)

    if continent:
        for location in locations:
            if location["fcode"] != "CONT" and location["name"] != "Earth":
                location["continent"] = continent
    
    added_locations = []
    for i, location in enumerate(locations):
        prev_location_id = added_locations[i-1] if i > 0 else None
        added_location = create_master_location(location, prev_location_id)
        added_locations.append(added_location)
        
    if added_locations[-1] is not None:
        match_locations(added_locations[-1], source_location)
    
    return added_locations
