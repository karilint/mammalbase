import datetime

from celery import shared_task
from mb.models import ViewMasterTraitValue, MasterEntity
import csv, zipfile, os, shutil
from django.core.files import File
from django.core.mail import send_mail
from .models import ExportFile
from datetime import datetime
from zipfile import ZipFile
from config import settings
from tempfile import mkdtemp
from django.db.models import Subquery, OuterRef, F

from mb.models import MasterEntity, EntityRelation, SourceEntity, EntityClass, SourceReference, MasterReference
from mb.models import SourceMeasurementValue, SourceAttribute, AttributeRelation, MasterAttribute, SourceUnit
from mb.models import UnitRelation, MasterUnit, SourceStatistic, UnitConversion
from tdwg.models import Taxon


@shared_task
def export_zip_file(query_data):
    """
    Exports a zip file containing tsv files resulting from given queries,
    saves it to the db and sends the download link as an email.

    Arguments:
    kwargs -- Dictionary containing fields
        email_receiver: str -- Email receiver
        queries: [dict] -- List of dictionaries containing fields
            file_name: str -- Desired name of the exported file
            headers: [str] -- List containing headers of data columns
            fields: [str] -- List containing desired data columns
            query_set: QuerySet -- QuerySet object to be executed
    """

    current_dir = os.getcwd()
    temp_directory = mkdtemp()
    os.chdir(temp_directory)

    zip_file_path = f'export_{datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f")}.zip'
    temp_zip_writer = ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED)

    for query in query_data['queries']:
        file_path = write_query_to_file(query)
        temp_zip_writer.write(file_path)

    temp_zip_writer.close()

    file_id = save_zip_to_django_model(zip_file_path)

    send_email(file_id, query_data['email_receiver'])

    os.chdir(current_dir)
    shutil.rmtree(temp_directory)


def write_query_to_file(query):
    """Used by export_zip_file()"""
    file_name = query['file_name']
    headers = query['headers']
    query_set = query['query_set']
    fields = query['fields']
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
def create_poc_tsv_file():
    export_zip_file({
        'email_receiver': 'testi@testipaikka.com',
        'queries': [
        {
            'file_name': 'ViewMasterTraitValue.objects.all',
            'headers': ['h1', 'h2', 'h3', 'etc...'],
            'query_set': ViewMasterTraitValue.objects.all()
        },
        {
            'file_name': 'ExportFile.objects.all',
             'headers': ['h1', 'h2', 'h3', 'etc...'],
             'query_set': ExportFile.objects.all()
        },
        {
            'file_name': 'MasterEntity.objects.all',
            'headers': ['h1', 'h2', 'h3', 'etc...'],
            'query_set': MasterEntity.objects.all()
        },
        ]})


@shared_task
def ets_export_query_set():

    master_attribute = AttributeRelation.objects.filter(
        source_attribute_id=OuterRef('source_attribute__id')
    )
    master_entity = EntityRelation.objects.filter(
        source_entity_id=OuterRef('source_entity__id')
    )
    unit_relation = UnitRelation.objects.filter(
        source_unit_id=OuterRef('source_unit__id')
    )
    unit_conversion = UnitConversion.objects.filter(
        from_unit=OuterRef('master_unit__id')
    )

    source_measurement_values = SourceMeasurementValue.objects.annotate(
        master_attribute__name=Subquery(
            master_attribute.values('master_attribute__name')[:1]
        ),
        master_attribute__id=Subquery(
            master_attribute.values('master_attribute__id')[:1]
        ),
        master_attribute__unit__id=Subquery(
            master_attribute.values('master_attribute__unit__id')[:1]
        ),
        master_entity__name=Subquery(
            master_entity.values('master_entity__name')[:1]
        ),
        master_entity__id=Subquery(
            master_entity.values('master_entity__id')[:1]
        ),
        master_unit__id=Subquery(
            unit_relation.values('master_unit__id')[:1]
        )
    ).annotate(
        unit_conversion__coefficient=Subquery(
            unit_conversion.filter(
                from_unit=OuterRef('master_unit__id'),
                to_unit=OuterRef('master_attribute_unit_id')
            )
        )
    ).exclude(
        master_attribute__name='- Checked, Unlinked -',
        (F('minimum')*F('unit_conversion__coefficient'))+(F('maximum')*F('unit_conversion__coefficient')) == 0
    )

    fields = [
        'master_attribute__name',
        'gender',
        'life_stage'
    ]
    headers = [
        'traitName',
        'gender',
        'life_stage'
    ]

    export_zip_file({
        'email_receiver': 'testi@testipaikka.com',
        'queries': [
            {
                'file_name': 'source_measurement_values',
                'headers': headers,
                'fields': fields,
                'query_set': source_measurement_values
            }
        ]
    })



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
