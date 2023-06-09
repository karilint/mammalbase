from django.db.models import Value, CharField
from django.db.models.functions import Concat
from exports.query_sets.measurements.base_query import query as base_query


query = base_query.annotate(
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