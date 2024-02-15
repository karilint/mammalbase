from django.db.models import Value, Case, When, CharField, Q
from .base_query import base_query
from mb.models.models import SourceChoiceSetOptionValue


def occurrence_query(measurement_choices):
    """
        Occurrence query function that defines the fields in the occurrence.tsv file 
        according to the ETS standard: https://ecologicaltraitdata.github.io/ETS/. 
        Values that are not yet in the models are set to 'NA'. 
        occurrence_ids that ends in -0-0-0 are excluded from the query. 
        Utilizes the base_query. Returns the query and fields whereof non active values
        are excluded.   
    """
    base = base_query(measurement_choices)

    non_active = (
          Q(gender__is_active=False)
        | Q(life_stage__is_active=False)
        | Q(source_location__is_active=False)
        | Q(source_statistic__is_active=False)
    )

    query = base.exclude(non_active).annotate(
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

    nominal_query = SourceChoiceSetOptionValue.objects.annotate(
        occurrence_id=Value('NA'),
        sex=Value('unknown'),
        life_stage=Value('adult'),
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
        verbatim_locality=Value('NA'),
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

    nominal_fields = [
        ('occurrence_id', 'occurrenceID'),
        ('sex', 'sex'),
        ('life_stage', 'lifeStage'),
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
        ('verbatim_locality', 'verbatimLocality'),
        ('country', 'country'),
        ('country_code', 'countryCode'),
        ('occurrence_remarks', 'occurrenceRemarks'),
    ]

    queries = []
    if "Nominal traits" in measurement_choices:
        queries.append((nominal_query, nominal_fields))
    
    if "Cranial measurements" in measurement_choices or "External measurements" in measurement_choices:
        queries.append((query, fields))

    return queries
