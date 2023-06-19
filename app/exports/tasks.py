import datetime
from celery import shared_task
import csv, zipfile, os, shutil
from django.core.files import File
from django.core.mail import send_mail
from .models import ExportFile
from datetime import datetime
from zipfile import ZipFile
from tempfile import mkdtemp
#from exports.query_sets.measurements import taxon_query, occurrence_query, measurement_or_fact_query, metadata_query #traitdata_query, traitlist_query
from config.settings import SITE_DOMAIN
from django.db.models import QuerySet

from exports.query_sets.measurements.traitlist_query import traitlist_query
from exports.query_sets.measurements.traitdata_query import traitdata_query
from exports.query_sets.measurements.taxon_query import taxon_query
from exports.query_sets.measurements.occurrence_query import occurrence_query
from exports.query_sets.measurements.metadata_query import metadata_query
from exports.query_sets.measurements.measurement_or_fact_query import measurement_or_fact_query


@shared_task
def export_zip_file(email_receiver: str, queries: list, export_file_id):
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
        export_file_id: -- id pointing to ExportFile instance where exported zip will be stored
    """
    if email_receiver == '':
        raise ValueError(
            'Expected argument email_receiver to contain an email address, got empty string instead'
        )
    if len(queries) == 0:
        raise ValueError(
            'Expected argument queries to contain at least one query, got empty list instead'
        )

    current_dir = os.getcwd()
    temp_directory = mkdtemp()
    os.chdir(temp_directory)

    zip_file_path = f'MammalBase_export_{datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f")}.zip'
    temp_zip_writer = ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED)

    for query in queries:
        try:
            file_path = write_query_to_file(**query)
        except (ValueError, TypeError):
            os.chdir(current_dir)
            shutil.rmtree(temp_directory)
            raise
        temp_zip_writer.write(file_path)

    temp_zip_writer.close()

    save_zip_to_django_model(zip_file_path, export_file_id)

    send_email(export_file_id, email_receiver)

    os.chdir(current_dir)
    shutil.rmtree(temp_directory)


def write_query_to_file(file_name: str, fields: list, query_set: QuerySet):
    """Used by export_zip_file()"""
    if file_name == '':
        raise ValueError(
            'Expected argument file_name to contain a name for export file, got empty string instead'
        )
    if len(fields) == 0:
        raise ValueError(
            'Expected query to contain at least one field, got empty list instead'
        )

    fields, headers = zip(*fields)
    file_path = f'{file_name}.tsv'
    f = open(file_path, 'w')
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerow(headers)
    writer.writerows(query_set.values_list(*fields))
    f.close()
    return file_path


def save_zip_to_django_model(zip_file_path: str, model_id):
    """Used by export_zip_file()"""
    with open(zip_file_path, 'rb') as zip_file:
        print(f'model_id = {model_id}')
        export_file = ExportFile.objects.get(pk=model_id)
        export_file.file = File(zip_file)
        export_file.save()
        zip_file.close()


@shared_task
def ets_export_query_set(user_email: str, export_file_id, is_admin_or_contributor: bool, measurement_choices):
    """Creates ETS-QuerySets."""
    def create_traitlist_queries(measurement_choices, queries):
        for measurement in measurement_choices:
            query_set, fields = traitlist_query([measurement])
            file_name = f'traitlist_{measurement.split()[0].lower()}'
            queries.append({
                'file_name': file_name,
                'fields': fields,
                'query_set': query_set
            })

    queries = []
    create_traitlist_queries(measurement_choices, queries)
    query, fields = traitdata_query(measurement_choices)
    queries.append({
            'file_name': 'traitdata',
            'fields': fields,
            'query_set': query
    })
    query, fields = taxon_query(measurement_choices)
    queries.append({
            'file_name': 'taxon',
            'fields': fields,
            'query_set': query
    })
    query, fields = occurrence_query(measurement_choices)
    queries.append({
            'file_name': 'occurrence',
            'fields': fields,
            'query_set': query
    })
    query, fields = metadata_query(measurement_choices)
    queries.append({
            'file_name': 'metadata',
            'fields': fields,
            'query_set': query
    })
    query, fields = measurement_or_fact_query(measurement_choices, is_admin_or_contributor)
    queries.append({
            'file_name': 'measurement_or_fact',
            'fields': fields,
            'query_set': query
    })

    export_zip_file(
        email_receiver=user_email,
        queries=queries,
        export_file_id=export_file_id
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
