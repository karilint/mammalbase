import os
import requests
from dotenv import load_dotenv

load_dotenv()

class LocationAPI:
    def __init__(self):
        self.geonames_username = os.getenv("GEONAMES_USERNAME")

    def get_locations(self, location_name):
        """
        Get the master location from the geonames API
        """
        url = f"http://api.geonames.org/searchJSON?q={location_name}&fuzzy=0.65&username={self.geonames_username}"
        response = requests.get(url)
        data = response.json()
        return data

    def get_nature_reserves(self, location_name):
        """
        Get the nature reserves from the geonames API
        """
        url = f"http://api.geonames.org/searchJSON?q={location_name}&username={self.geonames_username}"
        response = requests.get(url)
        data = response.json()
        if 'geonames' in data:
            nature_reservations = [place for place in data['geonames'] if place.get('fcode') == 'RESN' or place.get('fcode') == 'RESW' or place.get('fcode') == 'RESF']
            return nature_reservations
        else:
            return []

    def get_location_hierarchy(self, location_id):
        """
        Get the location hierarchy from the geonames API
        """
        url = f"http://api.geonames.org/hierarchyJSON?geonameId={location_id}&username={self.geonames_username}"
        response = requests.get(url)
        data = response.json()
        return data
