import datetime

from celery import shared_task
from mb.models import ViewMasterTraitValue
import csv, zipfile, os, shutil
from django.core.files import File
from django.core.mail import send_mail
from .models import ExportFile
from datetime import datetime
from django.db.models.query import QuerySet
from zipfile import ZipFile
from config import settings


@shared_task
def export_zip_file(queries: [(str, [str], QuerySet)]):
    temp_directory = f'temp_{datetime.now()}'
    os.mkdir(temp_directory)
    os.chdir(temp_directory)

    zip_file_path = f'export_{datetime.now()}.zip'
    temp_zip_writer = ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED)

    for file_name, headers, query in queries:
        file_path = write_query_to_file(file_name, headers, query)
        temp_zip_writer.write(file_path)

    temp_zip_writer.close()

    file_id = save_zip_to_django_model(zip_file_path)

    send_email(file_id, 'testi@testaaja.com')

    os.chdir('..')
    shutil.rmtree(temp_directory)


def write_query_to_file(file_name, headers, query):
    file_path = f'{file_name}.tsv'
    f = open(file_path, 'w')
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerow(headers)
    writer.writerows(query.values_list())
    f.close()
    return file_path


def save_zip_to_django_model(zip_file_path):
    with open(zip_file_path, 'rb') as zip_file:
        django_file = File(zip_file)
        file_model = ExportFile(file=django_file)
        file_model.save()
        return file_model.pk


@shared_task
def create_poc_tsv_file():
    export_zip_file([
        ('ViewMasterTraitValue.objects.all',
            ['h1', 'h2', 'h3', 'etc...'],
            ViewMasterTraitValue.objects.all()),
        ('ExportFile.objects.all',
            ['h1', 'h2', 'h3', 'etc...'],
            ExportFile.objects.all())
    ])


def zip_files(files):
    zip_file_name = f'export_{datetime.now()}.zip'
    temp_zip = ZipFile(zip_file_name, 'w', compression=zipfile.ZIP_DEFLATED)
    for file in files:
        temp_zip.write(file)
    temp_zip.close()
    return zip_file_name

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
