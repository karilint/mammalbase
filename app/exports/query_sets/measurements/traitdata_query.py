from django.db.models.functions import Concat
from django.db.models import CharField, Value, F, Case, When
from ..custom_db_functions import Round2
from exports.query_sets.measurements.base_query import base_query


def traitdata_query(measurement_choices):
    base = base_query(measurement_choices)

    query = base.annotate(
        trait_id=Concat(
            Value('https://www.mammalbase.net/ma/'),
            'source_attribute__master_attribute__id',
            Value('/'),
            output_field=CharField()
        ),
        trait_value=Round2(
            F('mean') * F('coefficient')
        ),
        verbatim_trait_value=Round2(
            F('mean')
        ),
        taxon_id=Concat(
            Value('https://www.mammalbase.net/me/'),
            'source_entity__master_entity__id',
            Value('/'),
            output_field=CharField()
        ),
        measurement_id=Concat(
            Value('https://www.mammalbase.net/smv/'),
            'id',
            Value('/'),
            output_field=CharField()
        ),
        occurrence_id=Value('NA'),
        warnings=Case(
            When(
                source_entity__master_entity__entity__name__iendswith='species',
                then=Value('NA')
            ),
            default=Concat(
                'source_entity__master_entity__entity__name',
                Value(' level data')
            )
        ),
    ).order_by(
        'source_attribute__master_attribute__name'
    )

    fields = [
        ('trait_id', 'traitID'),
        ('source_entity__master_entity__name', 'scientificName'),
        ('source_attribute__master_attribute__name', 'traitName'),
        ('trait_value', 'traitValue'),
        ('source_attribute__master_attribute__unit__print_name', 'traitUnit'),
        ('source_entity__name', 'verbatimScientificName'),
        ('source_attribute__name', 'verbatimTraitName'),
        ('verbatim_trait_value', 'verbatimTraitValue'),
        ('source_unit__name', 'verbatimTraitUnit'),
        ('taxon_id', 'taxonID'),
        ('measurement_id', 'measurementID'),
        ('occurrence_id', 'occurrenceID'),
        ('warnings', 'warnings'),
    ]

    return query, fields
