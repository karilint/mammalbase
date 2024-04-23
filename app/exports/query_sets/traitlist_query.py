from django.db.models import Value, CharField, Q, Case, When
from django.db.models.functions import Concat, Replace

from mb.models import MasterAttribute
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

    attributelink = {}
    attributes = MasterAttribute.objects.filter(groups__name='Nominal traits')
    for i in attributes:
        for j in i.masterchoicesetoption_set.all():
            try:
                attributelink[i.name].append(j.name)
            except:
                attributelink[i.name]=[j.name]

    nominal_query = MasterAttribute.objects.prefetch_related(
            'master_choiceset_option_set').filter(groups__name='Nominal traits').annotate(
        identifier=Concat(
            Value('https://www.mammalbase.net/ma/'),
            'id',
            Value('/'),
            output_field=CharField()
        ),
        trait=Replace(
            'name',
            Value(' '),
            Value('_')
        ),
        narrowerTerm=Value('NA'),
        relatedTerm=Value('NA'),
        factorLevels=Case(
            *[
            When(name=attribute_name, then=Value(
                ', '.join(attributelink[attribute_name]),output_field=CharField()
            )) for attribute_name in attributelink
            ]
        ),
        broaderTerm=Value('NA'),
        expectedUnit=Value('NA'),
        comments=Value('NA'),
    ).order_by(
        'groups__name',
        'attributegrouprelation__display_order'
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
        ('value_type', 'valueType'),
        ('expectedUnit', 'expectedUnit'),
        ('factorLevels', 'factorLevels'),
        ('max_allowed_value', 'maxAllowedValue'),
        ('min_allowed_value', 'minAllowedValue'),
        ('description', 'traitDescription'),
        ('comments', 'comments'),
        ('reference__citation', 'source')
    ]

    queries = []
    if "Nominal traits" in measurement_choices:
        queries.append((nominal_query, nominal_fields))

    if ("Cranial measurements" in
        measurement_choices or
        "External measurements" in
        measurement_choices):
        queries.append((query, fields))

    return queries
