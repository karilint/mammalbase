from mb.models import SourceLocation, MasterLocation, LocationRelation

def create_master_location(geoNamesLocation: dict):
    master_location = MasterLocation(name=geoNamesLocation["name"], reference="test")
    master_location.save()
    return master_location

def match_locations(sourceLocation, masterLocation):
    location_relation = LocationRelation(source_location_id=sourceLocation.id, master_location_id=masterLocation.id)
    location_relation.save()
    return location_relation