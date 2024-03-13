from matchtools.location_api import LocationAPI
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('location_name', type=str)
    
    def handle(self, *args, **options):
        location_name = options['location_name']
        api = LocationAPI()
        location = api.get_master_location(location_name)
        print("location:", location)
        geonameId = location[0]["geonameId"]
        
        if location:
            hierarchy = api.get_location_hierarchy(geonameId)
            print("hierarchy:", hierarchy)
        
        
        
        