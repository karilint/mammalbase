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
from django.db.models import Subquery, OuterRef, F, Value, CharField, ExpressionWrapper, FloatField
from django.db.models.functions import Concat

from mb.models import MasterEntity, EntityRelation, SourceEntity, EntityClass, SourceReference, MasterReference
from mb.models import SourceMeasurementValue, SourceAttribute, AttributeRelation, MasterAttribute, SourceUnit
from mb.models import UnitRelation, MasterUnit, SourceStatistic, UnitConversion
from tdwg.models import Taxon


@shared_task
def export_zip_file(email_receiver=None, queries=None):
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


def write_query_to_file(file_name=None, fields=None, query_set=None):
    """Used by export_zip_file()"""
    headers = list(map(lambda x: x[1], fields))
    fields = list(map(lambda x: x[0], fields))
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
    export_zip_file(
        email_receiver='testi@testipaikka.com',
        queries=[
        {
            'file_name': 'ViewMasterTraitValue.objects.all',
            'fields': [],
            'query_set': ViewMasterTraitValue.objects.all()
        },
        {
            'file_name': 'ExportFile.objects.all',
            'fields': [],
            'query_set': ExportFile.objects.all()
        },
        {
            'file_name': 'MasterEntity.objects.all',
            'fields': [],
            'query_set': MasterEntity.objects.all()
        },
        ])


@shared_task
def ets_export_query_set():

    source_measurement_values = SourceMeasurementValue.objects.annotate(
        coefficient=Subquery(
            UnitConversion.objects.filter(
                from_unit_id=OuterRef('source_unit__master_unit__id'),
                to_unit_id=OuterRef('source_attribute__master_attribute__unit')
            ).values_list('coefficient')[:1]
        )
    ).annotate(
        minplusmax=(F('minimum')*F('coefficient'))+(F('maximum')*F('coefficient'))
    ).exclude(
        source_attribute__master_attribute__name='- Checked, Unlinked -'
    ).exclude(
        minplusmax=0
    ).exclude(
        source_attribute__master_attribute__name__exact=''
    ).annotate(
        trait_id=Concat(
            Value('https://www.mammalbase.net/ma/'),
            'source_attribute__master_attribute__id',
            Value('/'),
            output_field=CharField()
        ),
        measurement_method=Value('NA'),
        measurement_determinedBy=Value('NA'),
        measurement_determinedDate=Value('NA'),
        measurement_remarks=Value('NA')
    ).order_by(
        'source_attribute__master_attribute__name'
    ).distinct()

    fields = [
        ('trait_id', 'traitID'),
        ('source_entity__master_entity__name','scientificName'),
        ('source_attribute__master_attribute__name', 'traitName'),
        ('measurement_method', 'measurementMethod'),
        ('measurement_determinedBy', 'measurementDeterminedBy'),
        ('measurement_determinedDate', 'measurementDeterminedDate'),
        ('measurement_remarks', 'measurementRemarks'),
    ]

    export_zip_file(
        email_receiver='testi@testipaikka.com',
        queries=[
            {
                'file_name': 'source_measurement_values',
                'fields': fields,
                'query_set': source_measurement_values
            }
        ]
    )



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
