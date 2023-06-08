from django.db.models import Subquery, OuterRef, F, Q, Value, CharField, Case, When, Func, Max, Exists
from django.db.models.functions import Concat, Replace, Now, TruncDate

from exports.query_sets.measurements.base_query import query as base_query
from exports.query_sets.custom_db_functions import Round2


MoF_query = base_query.annotate(
    measurement_id=Concat(
        Value('https://www.mammalbase.net/smv/'),
        'id',
        Value('/'),
        output_field=CharField()
    ),
    basis_of_record=Value('literatureData'),
    references=Replace(
        Replace(
            'source_entity__reference__master_reference__citation',
            Value('<i>'),
            Value('')
        ),
        Value('</i>'),
        Value('')
    ),
    measurement_resolution=Case(
        When(
            source_entity__master_entity__entity__name__iendswith='species',
            then=Value('NA')
        ),
        default=Concat(
            'source_entity__master_entity__entity__name',
            Value(' level data')
        )
    ),
    measurement_method=Value('NA'),
    measurement_determinedBy=Value('NA'),
    measurement_determinedDate=Value('NA'),
    measurement_remarks=Value('NA'),
    aggregate_measure=Case(
        When(
            n_total=1,
            then=Value('FALSE')
        ),
        default=Value('TRUE')
    ),
    individual_count=Case(
        When(
            n_total=0,
            then=Value('NA')
        ),
        default='n_total',
        output_field=CharField()
    ),
    dispersion=Case(
        When(
            std=0,
            then=Value('NA')
        ),
        default=Round2(
            F('std') * F('coefficient')
        ),
        output_field=CharField()
    ),
    measurement_value_min=Round2(
        F('minimum') * F('coefficient')
    ),
    measurement_value_max=Round2(
        F('maximum') * F('coefficient')
    ),
)

MoF_fields = [
    ('measurement_id','measurementID'),
    ('basis_of_record', 'basisOfRecord'),
    ('source_entity__reference__master_reference__type', 'basisOfRecordDescription'),
    ('references', 'references'),
    ('measurement_resolution', 'measurementResolution'),
    ('measurement_method', 'measurementMethod'),
    ('measurement_determinedBy', 'measurementDeterminedBy'),
    ('measurement_determinedDate', 'measurementDeterminedDate'),
    ('measurement_remarks', 'measurementRemarks'),
    ('aggregate_measure', 'aggregateMeasure'),
    ('individual_count', 'individualCount'),
    ('dispersion', 'dispersion'),
    ('measurement_value_min', 'measurementValue_min'),
    ('measurement_value_max', 'measurementValue_max'),
    ('measurement_accuracy', 'measurementAccuracy'),
    ('source_statistic__name', 'statisticalMethod'),
]
