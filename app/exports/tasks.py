import datetime

from celery import shared_task
from mb.models import ViewMasterTraitValue
import csv, zipfile, os, shutil
from django.core.files import File
from django.core.mail import send_mail
from .models import ExportFile
from datetime import datetime
from django.db.models.query import QuerySet
from config import settings


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
    send_email(file_model.pk, 'testi@testaaja.com')

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

@shared_task
def send_email(export_id, target_address):
    ''''Sends user an email with download link to exported data'''
    mail_subject = "Your download from Mammalbase is ready"
    message = create_message(export_id)
    send_mail ( 
        subject = mail_subject,
        message = message,
        from_email = settings.EMAIL_HOST_USER,
        recipient_list = [target_address], 
    )

def create_message(export_id):
    '''
    Creates email message and download link 
    '''    
    return f'You can download your exported data from http://localhost:8000/exports/get_file/{export_id}'
