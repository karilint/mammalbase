from django.db.models import Value, Q
from exports.query_sets.measurements.base_query import base_query


def occurrence_query(measurement_choices):
    base = base_query(measurement_choices)

    non_active = (
          Q(gender__is_active=False)
        | Q(life_stage__is_active=False)
        | Q(source_location__is_active=False)
        | Q(source_statistic__is_active=False)
    )

    query = base.exclude(non_active).annotate(
        occurrence_id=Value('NA'),
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
    ).distinct()

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
