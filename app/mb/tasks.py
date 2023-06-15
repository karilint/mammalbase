from celery import shared_task
from django.core.files import File
from datetime import datetime
import time
from config.settings import SITE_DOMAIN
from django.db.models import QuerySet
from itis.models import TaxonomicUnits
import itis.views as itis
import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

@shared_task
def update_db_from_itis():
    print("Starting automatic database update.")
    tsn_objects = TaxonomicUnits.objects.all()
    db_start_time = time.time()
    skipped_units = 0
    for iteration, taxonomic_unit in enumerate(tsn_objects, 1):
        action_start_time = time.time()
        result = itis.updateTSN(taxonomic_unit.tsn)
        timestamp = time.time()-action_start_time
        estimated_time = round((len(tsn_objects)-iteration) * (time.time()-db_start_time)/(iteration),2)
        if result:
            print(f"{taxonomic_unit} has been updated! {round(timestamp,2)}")
        else:
            skipped_units+=1
            print(f"{bcolors.WARNING}{taxonomic_unit} has NOT been updated! {round(timestamp,2)}{bcolors.ENDC}")
        print( f"{round((float(iteration)/len(tsn_objects))*100,2)}%\tEstimated time left: {estimated_time} seconds", end='\r')
    print(f"{len(tsn_objects) - skipped_units} out of {len(tsn_objects)} taxonomic units have been updated in the database. Spent time: {round(time.time()-db_start_time,2)}")
        

