import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
geonames_username = os.getenv("GEONAMES_USERNAME")
protected_planet_token = os.getenv("PROTECTED_PLANET_TOKEN")

class LocationAPI:

    def get_master_location_from_geonames(location_name):
        """
        Get the master location from the geonames API
        """
        url = f"http://api.geonames.org/searchJSON?q={location_name}&username={geonames_username}"
        response = requests.get(url)
        data = response.json()
        return data

    def get_master_location_from_protected_planet(location_name):
        """
        Get the master location from the protected planet API
        """
        url = f"https://api.protectedplanet.net/v3/countries?token={protected_planet_token}/name={location_name}"
        response = requests.get(url)
        data = response.json()
        return data