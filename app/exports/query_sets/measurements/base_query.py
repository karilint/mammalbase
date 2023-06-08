from django.db.models import Subquery, OuterRef, F, Q, Value, CharField, Case, When, Func, Max, Exists
from django.db.models.functions import Concat, Replace, Now, TruncDate
from allauth.socialaccount.models import SocialAccount

from mb.models import MasterEntity, DietSetItem, SourceEntity, EntityClass, SourceReference, MasterReference
from mb.models import SourceMeasurementValue, SourceAttribute, AttributeRelation, MasterAttribute, SourceUnit
from mb.models import UnitRelation, MasterUnit, SourceStatistic, UnitConversion
from tdwg.models import Taxon



query = SourceMeasurementValue.objects.annotate(
    coefficient=Subquery(
        UnitConversion.objects.filter(
            from_unit_id=OuterRef('source_unit__master_unit__id'),
            to_unit_id=OuterRef('source_attribute__master_attribute__unit')
        ).values_list('coefficient')[:1]
    )
).annotate(
    minplusmax=(F('minimum')*F('coefficient'))+(F('maximum')*F('coefficient'))
).exclude(
    source_attribute__master_attribute__name='- Checked, Unlinked -'
).exclude(
    minplusmax=0
).exclude(
    source_attribute__master_attribute__name__exact=''
).exclude(
    source_entity__master_entity__name__exact=''
).exclude(
    source_entity__master_entity__id__isnull=True
)

"""
version = DietSetItem.objects.aggregate(
    version=Max(TruncDate('modified_on'))
)['version']

query = SourceMeasurementValue.objects.annotate(
    coefficient=Subquery(
        UnitConversion.objects.filter(
            from_unit_id=OuterRef('source_unit__master_unit__id'),
            to_unit_id=OuterRef('source_attribute__master_attribute__unit')
        ).values_list('coefficient')[:1]
    )
).annotate(
    minplusmax=(F('minimum')*F('coefficient'))+(F('maximum')*F('coefficient'))
).exclude(
    source_attribute__master_attribute__name='- Checked, Unlinked -'
).exclude(
    minplusmax=0
).exclude(
    source_attribute__master_attribute__name__exact=''
).exclude(
    source_entity__master_entity__name__exact=''
).exclude(
    source_entity__master_entity__id__isnull=True
).annotate(
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
    kingdom=Value('Animalia'),
    phylum=Value('Chordata'),
    taxon_class=Value('Mammalia'),
    occurrence_id=Value('NA'),
    basis_of_record=Value('literatureData'),
    references=Replace(
        Replace(
            'source_entity__reference__master_reference__citation',
            Value('<i>'),
            Value('')
        ),
        Value('</i>'),
        Value('')
    ),
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
    measurement_method=Value('NA'),
    measurement_determinedBy=Value('NA'),
    measurement_determinedDate=Value('NA'),
    measurement_remarks=Value('NA'),
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
    orcid_uid=Subquery(
        SocialAccount.objects.filter(
            user_id=OuterRef('created_by__id')
        ).values_list('uid')[:1]
    ),
    issued=Now(),
    version=Value(version)
).annotate(
    author=Case(
        When(orcid_uid__startswith='http',
             then='orcid_uid'),
        default=Value('https://orcid.org/0000-0001-9627-8821')
    )
).order_by(
    'source_attribute__master_attribute__name'
).distinct()"""

fields = [
    ('trait_id', 'traitID'),
    ('source_entity__master_entity__name','scientificName'),
    ('source_attribute__master_attribute__name', 'traitName'),
    ('trait_value', 'traitValue'),
    ('source_attribute__master_attribute__unit__print_name','traitUnit'),
    ('source_entity__name','verbatimScientificName'),
    ('source_attribute__name','verbatimTraitName'),
    ('verbatim_trait_value','verbatimTraitValue'),
    ('source_unit__name','verbatimTraitUnit'),
    ('taxon_id','taxonID'),
    ('measurement_id','measurementID'),
    ('occurrence_id','occurrenceID'),
    ('warnings', 'warnings'),
    ('source_entity__master_entity__entity__name', 'taxonRank'),
    ('kingdom', 'kingdom'),
    ('phylum', 'phylum'),
    ('taxon_class', 'class'),
    ('source_entity__master_entity__taxon__order', 'order'),
    ('source_entity__master_entity__taxon__family', 'family'),
    ('source_entity__master_entity__taxon__genus', 'genus'),
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
    ('source_statistic__name', 'statisticalMethod'),
    ('author', 'author'),
    ('issued', 'issued'),
    ('version', 'version'),
]