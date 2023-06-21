from django.db.models import Value, CharField, Q
from django.db.models.functions import Concat
from exports.query_sets.measurements.base_query import base_query


def taxon_query(measurement_choices):
    base = base_query(measurement_choices)

    non_active = (
            Q(source_entity__master_entity__entity__is_active=False)
    )

    query = base.exclude(non_active).annotate(
            taxon_id=Concat(
            Value('https://www.mammalbase.net/me/'),
            'source_entity__master_entity__id',
            Value('/'),
            output_field=CharField()
        ),
        kingdom=Value('Animalia'),
        phylum=Value('Chordata'),
        taxon_class=Value('Mammalia'),
    ).order_by('source_entity__master_entity__taxon__sort_order').distinct()

    fields = [
        ('taxon_id','taxonID'),
        ('source_entity__master_entity__entity__name', 'taxonRank'),
        ('kingdom', 'kingdom'),
        ('phylum', 'phylum'),
        ('taxon_class', 'class'),
        ('source_entity__master_entity__taxon__order', 'order'),
        ('source_entity__master_entity__taxon__family', 'family'),
        ('source_entity__master_entity__taxon__genus', 'genus'),
    ]

    return query, fields
