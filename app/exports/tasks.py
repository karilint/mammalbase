import os
import shutil
from tempfile import mkdtemp

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from config.settings import SITE_DOMAIN
from django.db.models import QuerySet
from .models import ExportFile

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


def enter_temp_dir():
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
    export = ExportFile.objects.get(pk=export_id)
    current_date = export.created_on

    # Format the date as "7th August 2023"
    formatted_date = current_date.strftime("%d %B %Y")

    # Add "th" to the day if it's between 11 and 13 to handle exceptions
    if 11 <= current_date.day <= 13:
        formatted_date = formatted_date.replace(str(current_date.day), str(current_date.day) + "th")
    else:
        # Handle other day numbers with appropriate suffixes (st, nd, rd)
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(current_date.day % 10, 'th')
        formatted_date = formatted_date.replace(str(current_date.day), str(current_date.day) + suffix)

    # Print the text with the formatted date
    print(f"Accessed {formatted_date}")

    return f"""
Dear MammalBase User,

We hope this email finds you well. We are pleased to inform you that your requested data export from MammalBase is now ready for access. You can find the export file using the Ecological Traitdata Standard (ETS) format at the link provided at the end of this message.

The ETS format allows for the integration of the dataset into your research workflow. To learn more about the ETS terminology, please visit: https://terminologies.gfbio.org/terms/ets/pages/

At MammalBase, we remain dedicated to fostering research on mammalian traits and measurements, continually expanding our database with the latest findings to meet the needs of researchers like you.

As a part of our ongoing efforts to enhance the quality and scope of our database, we welcome contributions from the research community. Should you or your colleagues possess additional original, published trait and measurement data on mammals, we would be grateful to include it. For further inquiries, kindly contact Dr Kari Lintulaakso at kari.lintulaakso@helsinki.fi at the Finnish Museum of Natural History, and he will be pleased to provide a preformatted import template file in ETS format.

To cite the exported dataset, please include the following information:
The MammalBase community 2023. / CC BY 4.0. http://doi.org/10.5281/zenodo.7462864 Accessed {formatted_date} at https://mammalbase.org

To access your requested data, kindly use the following link: https://{SITE_DOMAIN}/exports/get_file/{export_id}

If you require any assistance or have inquiries about the data or our platform, please don't hesitate to contact our dedicated Team MammalBase.

We value your participation in the MammalBase community and appreciate your support in making this resource a valuable asset to researchers worldwide.

Best regards,

Team MammalBase
"""