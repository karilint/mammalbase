from mb.models import SourceLocation, MasterLocation, LocationRelation
from matchtools.location_api import LocationAPI

def create_master_location(geo_names_location: dict, hierarchy_location: MasterLocation = None):
    """
    Creates a master location from a GeoNames location.
    If the location is new, it is saved to the database.
    """

    # Extracting data from the GeoNames location
    name = geo_names_location["name"]
    latitude = geo_names_location["lat"]
    longitude = geo_names_location["lng"]
    location_id = geo_names_location["geonameId"]
    country = geo_names_location.get("countryName")
    country_code = geo_names_location.get("countryCode")
    continent = geo_names_location.get("continent")
    is_reserve = True if geo_names_location.get("fcode") in ["RESN", "RESW", "RESF"] else False

    # Creating or getting the master location
    master_location, created = MasterLocation.objects.get_or_create(
        name=name,
        decimal_latitude=latitude,
        decimal_longitude=longitude,
        location_id=location_id,
        is_reserve=is_reserve
    )

    # If the location is new, update its fields and save it
    if created:
        if country:
            master_location.country = country
            master_location.country_code = country_code

        if continent:
            master_location.continent = continent

        if hierarchy_location:
            master_location.higher_geography = hierarchy_location

        master_location.save()

    return (master_location, created)

def match_locations(master_location, source_location):
    """Adds a master and source location to the LocationRelation table."""

    if master_location is None:
        raise ValueError("master_location cannot be None")

    location_relation, _ = LocationRelation.objects.get_or_create(
        master_location=master_location,
        source_location=source_location,
    )
    return location_relation

def add_locations(geo_names_location, source_location_id):
    """adds a master location and it's hierarchy location(s) to the database"""

    source_location = SourceLocation.objects.get(id=source_location_id)
    api = LocationAPI()
    hierarchy_list = api.get_location_hierarchy(geo_names_location["geonameId"])["geonames"]

    # Filter out the duplicate GeoNames location from the hierarchy list
    hierarchy_list = [location for location in hierarchy_list if location["name"] != geo_names_location["name"]]

    locations = hierarchy_list + [geo_names_location]

    # Get the continent from the locations
    continent = next((location["name"] for location in locations if location["fcode"] == "CONT"), None)

    # If a continent is found, add it to the other locations
    if continent:
        for location in locations:
            if location["fcode"] != "CONT" and location["name"] != "Earth":
                location["continent"] = continent

    added_locations = []

    # Initialize hierarchy_location variable
    hierarchy_location = None

    # Loop over the locations and add them to the database
    for location in locations:
        master_location, created = create_master_location(location, hierarchy_location)

        # Adds the location to the added_locations list if it was a new location
        if created:
            added_locations.append(master_location)

        # Saves the higher hierarchy master_location
        # if it was created or it was in the database already
        hierarchy_location = master_location

    # Always include the final master location so the UI can display the
    # matched location even if it already existed in the database.
    if hierarchy_location is not None and (
        not added_locations or added_locations[-1] != hierarchy_location
    ):
        added_locations.append(hierarchy_location)

    # Match the source location with the final master location regardless of
    # whether it was newly created or already existed in the database.
    if hierarchy_location is not None:
        match_locations(hierarchy_location, source_location)

    return added_locations


def get_hierarchy_chain(master_location):
    """Return list of hierarchy names from continent to the given master location."""

    chain = []
    current = master_location
    while current is not None:
        chain.append(current)
        current = current.higher_geography

    chain.reverse()

    start_index = 0
    for i, loc in enumerate(chain):
        if loc.continent:
            start_index = i
            break

    return [loc.name for loc in chain[start_index:]]
