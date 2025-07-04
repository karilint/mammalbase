from django.db.models import Value, CharField, Q
from django.db.models.functions import Concat

from mb.models import SourceChoiceSetOptionValue
from .base_query import base_query

def taxon_query(measurement_choices):
    """
        Taxon query function that defines the fields in the taxon.tsv file
        according to the ETS standard: https://ecologicaltraitdata.github.io/ETS/.
        Utilizes the base query for measurement values and 
        a query using SourceChoiceSetOptionValue object for nominal values.
        taxon.tsv is sorted according to tdwg/taxon model's sort_order field.
        Returns the query and fields whereof non active values are excluded.
    """
    base = base_query(measurement_choices)

    non_active = (
            Q(source_entity__master_entity__entity__is_active=False)
          | Q(source_entity__master_entity__id=None)
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

    nominal_query = SourceChoiceSetOptionValue.objects.exclude(non_active).annotate(
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

    queries = []
    if "Nominal traits" in measurement_choices:
        queries.append((nominal_query, fields))

    if ("Cranial measurements" in
        measurement_choices or
        "External measurements" in
        measurement_choices):
        queries.append((query, fields))


    return queries