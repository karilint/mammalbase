from django.db.models import F, Value, CharField, Case, When
from django.db.models.functions import Concat, Replace
from exports.query_sets.custom_db_functions import Round2
from datetime import timezone, datetime, timedelta

from exports.query_sets.measurements.base_query import base_query

def measurement_or_fact_query(measurement_choices, is_admin_or_contributor):
    base = base_query(measurement_choices)

    now = str(datetime.now(tz=timezone(timedelta(hours=2))).strftime('%Y-%m-%d %H:%M:%S +02:00'))
    now2 = str(datetime.now(tz=timezone(timedelta(hours=2))).strftime('%d %m %Y'))

    if is_admin_or_contributor:
        query = base.annotate(
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

    else:
        query = base_query.annotate(
            measurement_id=Concat(
                Value('https://www.mammalbase.net/smv/'),
                'id',
                Value('/'),
                output_field=CharField()
            ),
            basis_of_record=Value('literatureData'),
            references=Concat(
                Value('The MammalBase community '),
                Value(now),
                Value(' , Data version '),
                Value(now2),
                Value(' at https://mammalbase.org/me/'),
                output_field=CharField()
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


    fields = [
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

    return query, fields
