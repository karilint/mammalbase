from django.db.models import F, Value, CharField, Case, When, Subquery, Min, Q
from django.db.models.functions import Concat, Replace
from exports.query_sets.custom_db_functions import Round2
from datetime import timezone, datetime, timedelta
from mb.models.models import SourceChoiceSetOptionValue

from .base_query import base_query

def measurement_or_fact_query(
        measurement_choice :str,
        is_admin_or_contributor: bool):
    """ Gather query and corresponding fields to satisfy the ETS standard.

    Keyword Arguments:
    measurement_choice -- entry name from MasterAttributeGroup
    is_admin_or_contributor -- admin/contirbutor status from mb/views

    Return Value:
    List with a (QuerySet, fields) tuple.

    Description:
    MOF query is function that defines the query and the fields to be later
    processed to the the measurement_or_fact_<choice>.tsv file according to
    the ETS standard: https://ecologicaltraitdata.github.io/ETS/.
    Utilizes the base_query. Values that are not yet in the models are set
    to 'NA'. References are determined by whether the user is
    a data_admin/data_contributor or other user. Returned query and fields
    depends whats in measurement_choice so that caller can make a file per
    a choice. measurement_or_fact_query returns the query and fields whereof
    non active values are excluded.
    """
    base = base_query([measurement_choice])


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
                default = mb_reference
        )

    nominal_query = SourceChoiceSetOptionValue.objects.annotate(
        entity_id=Concat(
            Value('http://localhost:8000/sav/'),
            'id',
            Value('/'),
            output_field=CharField()
        ),
        basis_of_record=Value('literatureData'),
        basis_of_record_description=F('source_entity__reference__master_reference__type'),
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
                source_choiceset_option__source_attribute__method__name__exact=None,
                then=Value('NA')
            ),
            default='source_choiceset_option__source_attribute__method__name',
            output_field=CharField()
        ),
        measurement_determinedBy=Value('NA'),
        measurement_determinedDate=Value('NA'),
        measurement_remarks=Value('NA'),
        aggregate_measure=Value('NA'),
        individual_count=Value('NA'),
        dispersion=Value('NA'),
        measurement_value_min=Value('NA'),
        measurement_value_max=Value('NA')
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

    if measurement_choice == "Nominal traits":
        # TODO: Find fields in query and export to spreadsheet here
        fields = [
            ('entity_id','traitID'),
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
            ('measurement_value_max', 'measurementValue_max')
        ]
        query = nominal_query
    elif measurement_choice in ('External measurements', 'Cranial measurements'):
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
    else:
        fields = [
            ("id",f'Unknown choice: {measurement_choice}')
        ]

    return [(query, fields)]
