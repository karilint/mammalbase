from django.db.models import F, Value, CharField, Case, When, Subquery, Min, Q
from django.db.models.functions import Concat, Replace
from exports.query_sets.custom_db_functions import Round2
from datetime import timezone, datetime, timedelta

from exports.query_sets.measurements.base_query import base_query

def measurement_or_fact_query(measurement_choices, is_admin_or_contributor):
    """ 
        MOF query function that defines the fields in the measurement_or_fact.tsv file 
        according to the ETS standard: https://ecologicaltraitdata.github.io/ETS/. 
        Utilizes the base_query. Values that are not yet in the models are set to 'NA'.
        References are determined by whether the user is a data_admin/data_contributor or 
        other user. measurement_or_fact query results are divided into different files 
        according to the user choices (measurement_choices in base_query). exports/tasks.py has a function create_measurement_or_fact_query() to create the different files.
        Returns the query and fields whereof non active values are excluded.
    """
    base = base_query(measurement_choices)

    non_active = (
          Q(source_entity__master_entity__entity__is_active=False)
        | Q(source_entity__reference__is_active=False)
        | Q(source_entity__reference__master_reference__is_active=False)
        | Q(source_statistic__is_active=False)
    )

    now = datetime.now(tz=timezone(timedelta(hours=2)))
    now_format_1 = now.strftime('%Y-%m-%d %H:%M:%S +02:00')
    now_format_2 = now.strftime('%d %m %Y')

    mb_reference = Concat(
        Value('The MammalBase community '),
        Value(now_format_1),
        Value(' , Data version '),
        Value(now_format_2),
        Value(' at https://mammalbase.net/me/'),
        output_field=CharField()
    )

    references = Replace(
        Replace(
            'source_entity__reference__master_reference__citation',
            Value('<i>'),
            Value('')
        ),
        Value('</i>'),
        Value('')
    )

    if not is_admin_or_contributor:
        references = Case(
            When(source_entity__reference__master_reference__is_public = True,
                then = references ),
                default = mammalbase_reference
        )

    query = base.exclude(non_active).annotate(
        measurement_id=Concat(
            Value('https://www.mammalbase.net/smv/'),
            'id',
            Value('/'),
            output_field=CharField()
        ),
        basis_of_record=Value('literatureData'),
        references=references,
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
        measurement_method=Case(
            When(
                source_attribute__method__name__exact=None,
                then=Value('NA')
            ),
            default='source_attribute__method__name',
            output_field=CharField()
        ),
        measurement_determinedBy=Value('NA'),
        measurement_determinedDate=Value('NA'),
        measurement_remarks=Case(
            When(
                remarks__exact=None,
                then=Value('NA')
            ),
            default='remarks',
            output_field=CharField()
        ),
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
        ('source_statistic__name', 'statisticalMethod')
    ]

    return query, fields