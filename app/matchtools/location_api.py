import os
import requests
import json

class LocationAPI:
    def __init__(self):
        self.geonames_username = os.getenv("GEONAMES_USERNAME")

    def get_master_location(self, location_name):
        """
        Get the master location from the geonames API
        """
        url = f"http://api.geonames.org/searchJSON?q={location_name}&fuzzy=0.65&username={self.geonames_username}"
        response = requests.get(url)
        data = response.json()
        return data
    
    def get_location_hierarchy(self, location_id):
        """
        Get the location hierarchy from the geonames API
        """
        url = f"http://api.geonames.org/hierarchyJSON?geonameId={location_id}&username={self.geonames_username}"
        response = requests.get(url)
        data = response.json()
        return data