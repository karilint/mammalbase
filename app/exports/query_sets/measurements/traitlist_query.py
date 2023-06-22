from django.db.models import Value, CharField, Q, Case, When
from django.db.models.functions import Concat, Replace
from exports.query_sets.measurements.base_query import base_query


def traitlist_query(measurement_choices):
    base = base_query(measurement_choices)

    non_active = (
              Q(source_attribute__master_attribute__unit__is_active=False)
            | Q(source_attribute__master_attribute__reference__is_active=False)
    )

    query = base.exclude(non_active).annotate(
        identifier=Concat(
            Value('https://www.mammalbase.net/ma/'),
            'source_attribute__master_attribute__id',
            Value('/'),
            output_field=CharField()
        ),
        trait=Replace(
            'source_attribute__master_attribute__name',
            Value(' '),
            Value('_')
        ),
        narrowerTerm=Value('NA'),
        relatedTerm=Value('NA'),
        factorLevels=Value('NA'),
        maxAllowedValue=Case(When(source_attribute__master_attribute__max_allowed_value__iexact=None,then=Value('NA')
            ),
            default='source_attribute__master_attribute__max_allowed_value',
            output_field=CharField()
            ),
        minAllowedValue=Case(When(source_attribute__master_attribute__min_allowed_value__iexact=None,then=Value('NA')
            ),
            default='source_attribute__master_attribute__min_allowed_value',
            output_field=CharField()
            ),
        comments=Case(When(source_attribute__master_attribute__remarks__iexact=None,then=Value('NA')
            ),
            default='source_attribute__master_attribute__remarks',
            output_field=CharField()
            ),
    ).order_by(
        'source_attribute__master_attribute__groups__name',
        'source_attribute__master_attribute__attributegrouprelation__display_order'
    ).distinct()

    fields = [
        ('identifier', 'identifier'),
        ('trait', 'trait'),
        ('source_attribute__master_attribute__groups__name', 'broaderTerm'),
        ('narrowerTerm', 'narrowerTerm'),
        ('relatedTerm', 'relatedTerm'),
        ('source_attribute__master_attribute__value_type', 'valueType'),
        ('source_attribute__master_attribute__unit__print_name', 'expectedUnit'),
        ('factorLevels', 'factorLevels'),
        ('maxAllowedValue', 'maxAllowedValue'),
        ('minAllowedValue', 'minAllowedValue'),
        ('source_attribute__master_attribute__description', 'traitDescription'),
        ('comments', 'comments'),
        ('source_attribute__master_attribute__reference__citation', 'source')
    ]

    return query, fields
