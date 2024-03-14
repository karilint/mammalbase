from django.db.models import Value, CharField, Q, Case, When, F
from django.db.models.functions import Concat, Replace

from mb.models import SourceChoiceSetOptionValue, MasterChoiceSetOption
from .base_query import base_query


def traitlist_query(measurement_choices):
    """ 
        Traitlist query function that defines the fields in the traitlist.tsv file 
        according to the ETS standard: https://ecologicaltraitdata.github.io/ETS/. 
        Utilizes the base query. Values that are not yet in the models are set to 'NA'. 
        Returns the query and fields whereof non active values are excluded.
    """
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
    ).order_by(
        'source_attribute__master_attribute__groups__name',
        'source_attribute__master_attribute__attributegrouprelation__display_order'
    ).distinct()

    nominal_query = SourceChoiceSetOptionValue.objects.annotate(
        identifier=Concat(
            Value('https://www.mammalbase.net/ma/'),
            'source_choiceset_option__source_attribute__master_attribute__id',
            Value('/'),
            output_field=CharField()
        ),
        trait=Replace(
            'source_choiceset_option__source_attribute__master_attribute__name',
            Value(' '),
            Value('_')
        ),
        narrowerTerm=Value('NA'),
        relatedTerm=Value('NA'),
        broaderTerm=Value('NA'),
        expectedUnit=Value('NA'),
        max_allowed_value=Value('NA'),
        min_allowed_value=Value('NA'),
        comments=Value('NA'),
    ).order_by(
        'source_choiceset_option__source_attribute__master_attribute__groups__name',
        'source_choiceset_option__source_attribute__master_attribute__attributegrouprelation__display_order'
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
        ('source_attribute__master_attribute__max_allowed_value', 'maxAllowedValue'),
        ('source_attribute__master_attribute__min_allowed_value', 'minAllowedValue'),
        ('source_attribute__master_attribute__description', 'traitDescription'),
        ('source_attribute__master_attribute__remarks', 'comments'),
        ('source_attribute__master_attribute__reference__citation', 'source')
    ]

    nominal_fields = [
        ('identifier', 'identifier'),
        ('trait', 'trait'),
        ('broaderTerm', 'broaderTerm'),
        ('narrowerTerm', 'narrowerTerm'),
        ('relatedTerm', 'relatedTerm'),
        ('source_choiceset_option__source_attribute__master_attribute__value_type', 'valueType'),
        ('expectedUnit', 'expectedUnit'),
        ('source_choiceset_option__master_choiceset_option__name', 'factorLevels'),
        ('max_allowed_value', 'maxAllowedValue'),
        ('min_allowed_value', 'minAllowedValue'),
        ('source_choiceset_option__source_attribute__master_attribute__description', 'traitDescription'),
        ('comments', 'comments'),
        ('source_choiceset_option__source_attribute__master_attribute__reference__citation', 'source')
    ]

    queries = []
    if "Nominal traits" in measurement_choices:
        queries.append((nominal_query, nominal_fields))
    
    if "Cranial measurements" in measurement_choices or "External measurements" in measurement_choices:
        queries.append((query, fields))

    return queries