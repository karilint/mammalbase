import os
import shutil
from tempfile import mkdtemp

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import QuerySet

from .models import ExportFile
from .utilities import (
        ExportFileWriter,
        generate_download_ready_message)
from .query_sets import (
        traitlist_query,
        traitdata_query,
        taxon_query,
        occurrence_query,
        metadata_query,
        measurement_or_fact_query)        


@shared_task
def export_zip_file(
        email_receiver: str,
        export_list: list,
        export_file_id,
        file_writer=ExportFileWriter()):
    """
    Exports a zip file containing tsv files resulting from given queries,
    saves it to the db and sends the download link as an email.

    Keyword arguments:
    email_receiver -- Email receiver address
    export_list -- List of dicts containing information for creating files
            ['file_name'] -- file_name to save queries to
            ['queries_and_fields'] -- queries and corresponding fields
    export_file_id -- id pointing to ExportFile instance where exported zip
                      will be stored
    file_writer -- dependency injection, this class is responsible for file
                   writing in exports
    """
    if email_receiver == '':
        raise ValueError(
            'Expected argument email_receiver to contain an email address, '
            'got empty string instead'
        )
    if len(export_list) == 0:
        raise ValueError(
            'Expected argument queries to contain at least one query, '
            'got empty list instead'
        )
    current_dir, temp_directory = enter_temp_dir()

    tsv_files = []
    for export_entry in export_list:
        try:
            file_path = write_queries_to_file(
                file_writer,
                export_entry['file_name'],
                export_entry['queries_and_fields']
            )
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


def enter_temp_dir():
    current_dir = os.getcwd()
    temp_directory = mkdtemp()
    os.chdir(temp_directory)
    return current_dir, temp_directory


def exit_temp_dir(current_dir, temp_directory):
    os.chdir(current_dir)
    shutil.rmtree(temp_directory)


def write_queries_to_file( 
        file_writer,
        file_name: str,
        queries_and_fields: list):
    """Used by export_zip_file, writes a list of query results to tsv file"""

    def replace_na(values_list):
        """Helper function for replacing empty strings and Nones with NA on
        data returned by QuerySet.values_list()
        """
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


    if file_name == '':
        raise ValueError(
            'Expected argument file_name to contain a name for export file, '
            'got empty string instead'
        )
    if len(queries_and_fields) == 0:
        raise ValueError(
            'Expected query to contain at least one query, '
            'got empty list instead'
        )

    # Get headers from first entrys fields list
    _, headers = zip(*queries_and_fields[0][1])

    rows=[]
    for query_set, fields in queries_and_fields:
        if len(queries_and_fields) == 0:
            raise ValueError(
                'Expected fields to contain at least one field, '
                'got empty list instead'
            )
        fields, check_headers = zip(*fields)
        if len(headers) != len(check_headers):
            raise ValueError(
                'Count of header fields doesn\'t match across queries.'
            )
        for i in range(len(headers)):
            if headers[i] != check_headers[i]:
                raise ValueError(
                    'Headers fields are not same on queries. '
                    f"'{headers[i]}' vs '{check_headers[i]}'"
                )
        rows.extend(replace_na(query_set.values_list(*fields)))

    # TODO: Remove duplicate lines

    file_path = f'{file_name}.tsv'
    file_writer.write_rows(file_path, headers, rows)
    return file_path


@shared_task
def ets_export_query_set(
        user_email: str,
        export_file_id,
        is_admin_or_contributor: bool,
        measurement_choices: list):
    """Creates ETS-QuerySets.
    
    Keyword arguments:
    user_email -- Email where to send the download link
    export_file_id -- id pointing to ExportFile instance where exported zip
                will be stored
    is_admin_or_contributor -- Whether current user is in admin or
                datacontributor groups
    measurement_choices -- List of strings selected from export page. Valid
                options can be found at MasterAttributeGroup
    """

    export_list = []

    for measurement in measurement_choices:
        export_list.append({
                'file_name': ('measurement_or_fact_'
                        f'{measurement.split()[0].lower()}'),
                'queries_and_fields': measurement_or_fact_query([measurement],
                        is_admin_or_contributor) })

    for file_name, query_function in {
            'traitdata': traitdata_query,
            'traitlist': traitlist_query,
            'taxon': taxon_query,
            'occurrence': occurrence_query,
            'metadata': metadata_query }.items():
        export_list.append({
                'file_name': file_name,
                'queries_and_fields': query_function(measurement_choices) })

    export_zip_file(
        email_receiver=user_email,
        export_list=export_list,
        export_file_id=export_file_id
    )


@shared_task
def send_email(export_id, target_address):
    """Sends user an email with a download link to the exported data"""
    send_mail (
        subject = "MammalBase Data Export: Access Now Available",
        message = generate_download_ready_message(export_id),
        from_email = None,
        recipient_list = [target_address],
    )
