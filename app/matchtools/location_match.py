from mb.models import SourceLocation, MasterLocation, LocationRelation

def create_master_location(geoNamesLocation: dict):
    name = geoNamesLocation["name"]
    latitude = geoNamesLocation["lat"]
    longitude = geoNamesLocation["lng"]
    location_id = geoNamesLocation["geonameId"]
    country = geoNamesLocation.get("countryName")
    country_code = geoNamesLocation.get("countryCode")

    master_location = MasterLocation(name=name, decimal_latitude=latitude, decimal_longitude=longitude, location_id=location_id)
    if country:
        master_location.country = country
        master_location.country_code = country_code

    master_location.save()
    return master_location

def match_locations(sourceLocationId, masterLocationId):
    location_relation = LocationRelation(source_location_id=sourceLocationId, master_location_id=masterLocationId)
    location_relation.save()
    return location_relation