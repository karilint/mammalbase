import datetime
from celery import shared_task
import csv, zipfile, os, shutil
from django.core.files import File
from django.core.mail import send_mail
from .models import ExportFile
from datetime import datetime
from zipfile import ZipFile
from tempfile import mkdtemp
from exports.query_sets.measurements import taxon_query, occurrence_query, traitlist_query, measurement_or_fact_query, metadata_query, traitdata_query
from config.settings import SITE_DOMAIN
from django.db.models import QuerySet



@shared_task
def export_zip_file(email_receiver: str, queries: [dict]):
    """
    Exports a zip file containing tsv files resulting from given queries,
    saves it to the db and sends the download link as an email.

    Keyword arguments:
        email_receiver: str -- Email receiver address
        queries: [dict] -- List of dictionaries containing fields
            file_name: str -- Desired name of the exported file
            fields: [(str, str)] -- List of tuples containing desired data fields
                                    at [0] and corresponding column name at [1]
            query_set: QuerySet -- QuerySet object to be executed
    """


    current_dir = os.getcwd()
    temp_directory = mkdtemp()
    os.chdir(temp_directory)

    zip_file_path = f'export_{datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f")}.zip'
    temp_zip_writer = ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED)

    for query in queries:
        file_path = write_query_to_file(**query)
        temp_zip_writer.write(file_path)

    temp_zip_writer.close()

    file_id = save_zip_to_django_model(zip_file_path)

    send_email(file_id, email_receiver)

    os.chdir(current_dir)
    shutil.rmtree(temp_directory)


def write_query_to_file(file_name: str, fields: [(str, str)], query_set: QuerySet):
    """Used by export_zip_file()"""
    fields, headers = zip(*fields)
    file_path = f'{file_name}.tsv'
    f = open(file_path, 'w')
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerow(headers)
    writer.writerows(query_set.values_list(*fields))
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
def ets_export_query_set(user_email='testi.testaaja@testimaailma.fi'):

    export_zip_file(
        email_receiver=user_email,
        queries=[
            {
                'file_name': 'traitdata',
                'fields': traitdata_query.fields,
                'query_set': traitdata_query.query
            },
                        {
                'file_name': 'metadata',
                'fields': metadata_query.fields,
                'query_set': metadata_query.query
            },
                        {
                'file_name': 'measurement_or_fact',
                'fields': measurement_or_fact_query.fields,
                'query_set': measurement_or_fact_query.query
            },
                        {
                'file_name': 'occurrence',
                'fields': occurrence_query.fields,
                'query_set': occurrence_query.query
            },
                        {
                'file_name': 'taxon',
                'fields': taxon_query.fields,
                'query_set': taxon_query.query
            },
            {
                'file_name': 'traitlist',
                'fields': traitlist_query.fields,
                'query_set': traitlist_query.query
            }
        ]
    )


@shared_task
def send_email(export_id, target_address):
    """Sends user an email with a download link to the exported data"""
    mail_subject = "Your export from Mammalbase is ready"
    message = create_notification_message(export_id)
    send_mail (
        subject = mail_subject,
        message = message,
        from_email = None,
        recipient_list = [target_address],
    )

def create_notification_message(export_id):
    """Creates a email message and download link to the exported data"""
    return f"""
        Hello,

        The data you requested has been processed and can be accessed from https://{SITE_DOMAIN}/exports/get_file/{export_id}
        
        Kind regards,
        
        Team MammalBase
        """
