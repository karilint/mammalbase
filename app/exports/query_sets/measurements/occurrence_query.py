from django.db.models import Subquery, OuterRef, F, Q, Value, CharField, Case, When, Func, Max, Exists
from django.db.models.functions import Concat, Replace, Now, TruncDate

from exports.query_sets.measurements.base_query import query as base_query
from exports.query_sets.custom_db_functions import Round2

occurrence_query = base_query.annotate(
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

occurrence_fields = [
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