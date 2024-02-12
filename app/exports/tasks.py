import datetime
import os
import shutil
from tempfile import mkdtemp

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from config.settings import SITE_DOMAIN
from django.db.models import QuerySet

from .models import ExportFile
from .utilities.export_file_writer import ExportFileWriter
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
    mail_subject = "MammalBase Data Export: Access Now Available"
    message = create_notification_message(export_id)
    send_mail (
        subject = mail_subject,
        message = message,
        from_email = None,
        recipient_list = [target_address],
    )

def create_notification_message(export_id):
    """Creates an email message and download link to the exported data"""
#    export = ExportFile.objects.get(pk=export_id)
    current_date = datetime.date.today()

    # Format the date as "7th August 2023"
    formatted_date = current_date.strftime("%d %B %Y")

    # Add "th" to the day if it's between 11 and 13 to handle exceptions
    if 11 <= current_date.day <= 13:
        formatted_date = formatted_date.replace(
                str(current_date.day),
                str(current_date.day) + "th")
    else:
        # Handle other day numbers with appropriate suffixes (st, nd, rd)
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(current_date.day % 10, 'th')
        formatted_date = formatted_date.replace(
                str(current_date.day),
                str(current_date.day) + suffix)

    # Print the text with the formatted date
    print(f"Accessed {formatted_date}")

    return f"""
Dear MammalBase User,

We hope this email finds you well. We are pleased to inform you that your
requested data export from MammalBase is now ready for access. You can find
the export file using the Ecological Traitdata Standard (ETS) format at the
link provided at the end of this message.

The ETS format allows for the integration of the dataset into your research
workflow. To learn more about the ETS terminology, please visit:
https://terminologies.gfbio.org/terms/ets/pages/

At MammalBase, we remain dedicated to fostering research on mammalian traits
and measurements, continually expanding our database with the latest findings
to meet the needs of researchers like you.

As a part of our ongoing efforts to enhance the quality and scope of our
database, we welcome contributions from the research community. Should you or
your colleagues possess additional original, published trait and measurement
data on mammals, we would be grateful to include it. For further inquiries,
kindly contact Dr Kari Lintulaakso at kari.lintulaakso@helsinki.fi at the
Finnish Museum of Natural History, and he will be pleased to provide
a preformatted import template file in ETS format.

To cite the exported dataset, please include the following information:
The MammalBase community 2023. / CC BY 4.0.
http://doi.org/10.5281/zenodo.7462864
Accessed {formatted_date} at https://mammalbase.net

To access your requested data, kindly use the following link:
https://{SITE_DOMAIN}/exports/get_file/{export_id}

If you require any assistance or have inquiries about the data or our
platform, please don't hesitate to contact our dedicated Team MammalBase.

We value your participation in the MammalBase community and appreciate your
support in making this resource a valuable asset to researchers worldwide.

Best regards,

Team MammalBase
"""