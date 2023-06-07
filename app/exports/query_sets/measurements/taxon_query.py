from django.db.models import Subquery, OuterRef, F, Q, Value, CharField, Case, When, Func, Max, Exists
from django.db.models.functions import Concat, Replace, Now, TruncDate

from exports.query_sets.measurements.base_query import query as base_query


taxon_query = base_query.annotate(
        taxon_id=Concat(
        Value('https://www.mammalbase.net/me/'),
        'source_entity__master_entity__id',
        Value('/'),
        output_field=CharField()
     ),
     kingdom=Value('Animalia'),
     phylum=Value('Chordata'),
     taxon_class=Value('Mammalia'),
).distinct()

taxon_fields = [
    ('taxon_id','taxonID'),
    ('source_entity__master_entity__entity__name', 'taxonRank'),
    ('kingdom', 'kingdom'),
    ('phylum', 'phylum'),
    ('taxon_class', 'class'),
    ('source_entity__master_entity__taxon__order', 'order'),
    ('source_entity__master_entity__taxon__family', 'family'),
    ('source_entity__master_entity__taxon__genus', 'genus'),
]