import datetime

from celery import shared_task
from mb.models import ViewMasterTraitValue
import csv, zipfile, os, shutil
from django.core.files import File
from .models import ExportFile
from datetime import datetime
from django.db.models.query import QuerySet


@shared_task
def export_zip_file(queries: [QuerySet]):
    files = []
    temp_directory = f'temp_{datetime.now()}'
    os.mkdir(temp_directory)
    for i, query in enumerate(queries):
        file_path = f'{temp_directory}/export_{i}.tsv'
        with open(file_path, 'w') as f:
            files.append(file_path)
            writer = csv.writer(f, delimiter='\t', lineterminator='\n')
            writer.writerows(query().values_list())
    temp_zip_file_path = zip_files(files)
    with open(temp_zip_file_path, 'rb') as zip_file:
        django_file = File(zip_file)
        file_model = ExportFile(file=django_file)
        file_model.save()
        print(f'Created new file: http://localhost:8000/exports/get_file/{file_model.pk}')
    os.remove(temp_zip_file_path)
    shutil.rmtree(temp_directory)


@shared_task
def create_poc_tsv_file():
    export_zip_file([ViewMasterTraitValue.objects.all , ExportFile.objects.all])


def zip_files(files):
    file_name = f'export_{datetime.now()}.zip'
    temp_zip = zipfile.ZipFile(file_name, 'w', compression=zipfile.ZIP_DEFLATED)
    for file in files:
        temp_zip.write(file)
    temp_zip.close()
    return file_name

