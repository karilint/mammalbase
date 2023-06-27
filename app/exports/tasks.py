import os
import shutil
from tempfile import mkdtemp

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from config.settings import SITE_DOMAIN
from django.db.models import QuerySet

from exports.query_sets.measurements.traitlist_query import traitlist_query
from exports.query_sets.measurements.traitdata_query import traitdata_query
from exports.query_sets.measurements.taxon_query import taxon_query
from exports.query_sets.measurements.occurrence_query import occurrence_query
from exports.query_sets.measurements.metadata_query import metadata_query
from exports.query_sets.measurements.measurement_or_fact_query import measurement_or_fact_query

from .utilities.export_file_writer import ExportFileWriter


@shared_task
def export_zip_file(email_receiver: str, queries: list, export_file_id, file_writer=ExportFileWriter()):
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
        export_file_id -- id pointing to ExportFile instance where exported zip will be stored
        file_writer -- dependency injection, this class is responsible for file writing in exports
    """
    if email_receiver == '':
        raise ValueError(
            'Expected argument email_receiver to contain an email address, got empty string instead'
        )
    if len(queries) == 0:
        raise ValueError(
            'Expected argument queries to contain at least one query, got empty list instead'
        )
    current_dir, temp_directory = enter_temp_dir()

    tsv_files = []
    for query in queries:
        try:
            file_path = write_query_to_file(file_writer, **query)
        except (ValueError, TypeError):
            exit_temp_dir(current_dir, temp_directory)
            raise
        tsv_files.append(file_path)

    file_writer.zip(tsv_files)
    try:
        file_writer.save_zip_to_django_model(export_file_id)
    except (ObjectDoesNotExist, FileNotFoundError):
        exit_temp_dir(current_dir, temp_directory)
        raise

    send_email(export_file_id, email_receiver)

    exit_temp_dir(current_dir, temp_directory)


def enter_temp_dir() -> tuple[str, str]:
    current_dir = os.getcwd()
    temp_directory = mkdtemp()
    os.chdir(temp_directory)
    return current_dir, temp_directory


def exit_temp_dir(current_dir, temp_directory):
    os.chdir(current_dir)
    shutil.rmtree(temp_directory)


def write_query_to_file(file_writer, file_name: str, fields: list, query_set: QuerySet):
    """Used by export_zip_file, writes a single query result to tsv file"""
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
    file_writer.write_rows(file_path, headers, replace_na(query_set.values_list(*fields)))
    return file_path


def replace_na(values_list):
    """Takes an iterable from values_list method of a QuerySet instance and replaces empty strings or Nones with NA"""
    values_list = list(values_list)
    for i, row in enumerate(values_list):
        new_row = []
        for item in row:
            if item in ['', None]:
                new_row.append('NA')
            else:
                new_row.append(item)
        values_list[i] = tuple(new_row)
    return values_list


@shared_task
def ets_export_query_set(user_email: str, export_file_id, is_admin_or_contributor: bool, measurement_choices):
    """Creates ETS-QuerySets."""

    def create_measurement_or_fact_queries(measurement_choices, queries):
        """divides the measurement or fact query into separate queries and files according
        to user choices

        Args:
            measurement_choices [str]: list of strings containing user choices
            queries [QuerySet]: list containing QuerySets used in ETS export
        """
        for measurement in measurement_choices:
            query_set, fields = measurement_or_fact_query([measurement], is_admin_or_contributor)
            file_name = f'measurement_or_fact_{measurement.split()[0].lower()}'
            queries.append({
                'file_name': file_name,
                'fields': fields,
                'query_set': query_set
            })

    queries = []
    create_measurement_or_fact_queries(measurement_choices, queries)

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
    query, fields = traitlist_query(measurement_choices)
    queries.append({
            'file_name': 'traitlist',
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
    mail_subject = "Your export from MammalBase is ready"
    message = create_notification_message(export_id)
    send_mail (
        subject = mail_subject,
        message = message,
        from_email = None,
        recipient_list = [target_address],
    )

def create_notification_message(export_id):
    """Creates an email message and download link to the exported data"""
    return f"""
        Hello,

        The data you requested has been processed and can be accessed from https://{SITE_DOMAIN}/exports/get_file/{export_id}

        Kind regards,

        Team MammalBase
        """