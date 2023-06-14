from celery import shared_task
from django.core.files import File
from datetime import datetime
from config.settings import SITE_DOMAIN
from django.db.models import QuerySet
from itis.models import TaxonomicUnits
import itis.views as itis

@shared_task
def update_db_from_itis():
    tsn_objects = TaxonomicUnits.objects.all()
    for taxonomic_unit in tsn_objects:
        itis.updateTSN(taxonomic_unit.tsn)
        

