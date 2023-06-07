import datetime

from celery import shared_task
from mb.models import ViewMasterTraitValue
import csv, zipfile, os, shutil
from django.core.files import File
from django.core.mail import send_mail
from .models import ExportFile
from datetime import datetime
from zipfile import ZipFile
from config import settings
from tempfile import mkdtemp


@shared_task
def export_zip_file(kwargs):
    """
    Exports a zip file containing tsv files resulting from given queries,
    saves it to the db and sends the download link as an email.

    Arguments:
    kwargs -- Dictionary containing fields
        email_receiver: str -- Email receiver
        queries: [dict] -- List of dictionaries containing fields
            file_name: str -- Desired name of the exported file
            headers: [str] -- List containing headers of data columns
            query_set: QuerySet -- QuerySet object to be executed
    """

    current_dir = os.getcwd()
    temp_directory = mkdtemp()
    os.chdir(temp_directory)

    zip_file_path = f'export_{datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f")}.zip'
    temp_zip_writer = ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED)

    for query in kwargs['queries']:
        file_path = write_query_to_file(query)
        temp_zip_writer.write(file_path)

    temp_zip_writer.close()

    file_id = save_zip_to_django_model(zip_file_path)

    send_email(file_id, kwargs['email_receiver'])

    os.chdir(current_dir)
    shutil.rmtree(temp_directory)


def write_query_to_file(query):
    """Used by export_zip_file()"""
    file_name = query['file_name']
    headers = query['headers']
    query_set = query['query_set']
    file_path = f'{file_name}.tsv'
    f = open(file_path, 'w')
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerow(headers)
    writer.writerows(query_set.values_list())
    f.close()
    return file_path


def save_zip_to_django_model(zip_file_path):
    """Used by export_zip_file()"""
    with open(zip_file_path, 'rb') as zip_file:
        django_file = File(zip_file)
        file_model = ExportFile(file=django_file)
        file_model.save()
        zip_file.close()
        return file_model.pk


@shared_task
def create_poc_tsv_file(email_receiver):
    export_zip_file({
        'email_receiver': email_receiver,
        'queries': [{'file_name': 'ViewMasterTraitValue.objects.all',
                     'headers': ['h1', 'h2', 'h3', 'etc...'],
                     'query_set': ViewMasterTraitValue.objects.all()},
                    {'file_name': 'ExportFile.objects.all',
                     'headers': ['h1', 'h2', 'h3', 'etc...'],
                     'query_set': ExportFile.objects.all()}
                    ]})


@shared_task
def send_email(export_id, target_address):
    """Sends user an email with a download link to the exported data"""
    mail_subject = "Your download from Mammalbase is ready"
    message = create_notification_message(export_id)
    send_mail (
        subject = mail_subject,
        message = message,
        from_email = None,
        recipient_list = [target_address],
    )

def create_notification_message(export_id):
    """Creates a email message and download link to the exported data"""
    return f'You can download the exported data from http://localhost:8000/exports/get_file/{export_id}'
