from django.db.models import Value, CharField
from django.db.models.functions import Concat, Replace
from exports.query_sets.measurements.base_query import query as base_query


query = base_query.annotate(
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
    maxAllowedValue=Value('NA'),
    minAllowedValue=Value("NA"),
    comments=Value('NA')
)

fields = [
    ('identifier', 'identifier'),
    ('trait', 'trait'),
    ('source_attribute__master_attribute__attributegrouprelation__group__name', 'broaderTerm'),
    ('narrowerTerm', 'narrowerTerm'),
    ('relatedTerm', 'relatedTerm'),
    ('source_unit__master_unit__quantity_type', 'valueType'),
    ('source_unit__master_unit__print_name', 'expectedUnit'),
    ('factorLevels', 'factorLevels'),
    ('maxAllowedValue', 'maxAllowedValue'),
    ('minAllowedValue', 'minAllowedValue'),
    ('source_attribute__master_attribute__remarks', 'traitDescription'),
    ('comments', 'comments'),
    ('source_attribute__master_attribute__reference__citation', 'source')
]