import datetime
import random

from celery import shared_task
from mb.models import ViewMasterTraitValue
import csv
from django.core.files import File
from .models import ExportFile
from django.core.files.base import ContentFile


@shared_task
def hello_world_celery():
    print('Hello from the Celery world!')


@shared_task
def create_poc_tsv_file():
    measurements = ViewMasterTraitValue.objects.all()
    msr = measurements.values_list('id', 'master_id', 'master_entity_name', "master_attribute_id",
                                   'master_attribute_name', 'traits_references', 'assigned_values', 'n_distinct_value',
                                   'n_value', 'n_supporting_value', 'trait_values', 'trait_selected',
                                   'trait_references', 'value_percentage')
    filename = f'export_measurements_{random.randint(0,32000)}.tsv'
    with open(filename, 'w+') as f:
        django_file = File(f)
        writer = csv.writer(django_file, delimiter='\t', lineterminator='\n')
        writer.writerow(
            ['id', 'master_id', 'master_entity_name', 'master_attribute_id', 'master_attribute_name', 'traits_references',
            'assigned_values', 'n_distinct_value', 'n_value', 'n_supporting_value', 'trait_values', 'trait_selected',
            'trait_references', 'value_percentage'])
        for m in msr:
            writer.writerow(m)
        file_model = ExportFile(name=filename, file=django_file)
        file_model.save()
        print(f'Created new file. ID = {file_model.pk}')
