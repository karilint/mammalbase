from django.db.models import Value, CharField, When, Case
from django.db.models.functions import Concat
from exports.query_sets.measurements.base_query import base_query
from mb.models import SourceMeasurementValue


def occurrence_query(measurement_choices):
    base = base_query(measurement_choices)

    query = base.annotate(
        occurrence_id=Concat(
        Case(When(source_entity__id__iexact=None, then=Value('0')), 
            default='source_entity__id',
            output_field=CharField()),
            Value('-'),
            Case(When(source_location__id__iexact=None, then=Value('0')), 
            default='source_location__id',
            output_field=CharField()),
            Value('-'),
            Case(When(gender__id__iexact=None, then=Value('0')), 
            default='gender__id',
            output_field=CharField()),
            Value('-'),
            Case(When(life_stage__id__iexact=None, then=Value('0')), 
            default='life_stage__id',
            output_field=CharField())
        ),
        age=Value('NA'),
        morphotype=Value('NA'),
        event_id=Value('NA'),
        preparations=Value('NA'),
        sampling_protocol=Value('NA'), 
        year = Value('NA'),
        month=Value('NA'),
        day=Value('NA'),
        event_date=Value('NA'),
        location_id=Value('NA'),
        habitat=Value('NA'),
        decimal_longitude=Value('NA'), 
        decimal_latitude=Value('NA'),
        elevation=Value('NA'),
        geodetic_datum=Value('NA'),
        country=Value('NA'),
        country_code=Value('NA'), 
        occurrence_remarks=Value('NA')
    ).distinct().exclude(occurrence_id__endswith='-0-0-0')

    fields = [ 
        ('occurrence_id', 'occurrenceID'),
        ('gender__caption', 'sex'),
        ('life_stage__caption', 'lifeStage'),
        ('age', 'age'),
        ('morphotype', 'morphotype'),
        ('event_id', 'eventID'),
        ('preparations', 'preparations'),
        ('sampling_protocol', 'samplingProtocol'),
        ('year', 'year'),
        ('month', 'month'),
        ('day', 'day'),
        ('event_date', 'eventDate'),
        ('location_id', 'locationID'),
        ('habitat', 'habitat'),
        ('decimal_longitude', 'decimalLongitude'),
        ('decimal_latitude', 'decimalLatitude'),
        ('elevation', 'elevation'),
        ('geodetic_datum', 'geodeticDatum'),
        ('source_location__name', 'verbatimLocality'),
        ('country', 'country'),
        ('country_code', 'countryCode'),
        ('occurrence_remarks', 'occurrenceRemarks'),
    ]

    return query, fields