from django.db.models.functions import Concat
from django.db.models import CharField, Value, F, Case, When, Q

from mb.models import SourceChoiceSetOptionValue
from .custom_db_functions import Round2
from .base_query import base_query


def traitdata_query(measurement_choices):
    """
        Traitdata query function that defines the fields in the traitdata.tsv file
        according to the ETS standard: https://ecologicaltraitdata.github.io/ETS/.
        Utilizes the base_query. Returns the query and fields whereof non active values
        are excluded.
    """
    base = base_query(measurement_choices)

    non_active = (
            Q(source_attribute__master_attribute__unit__is_active=False)
    )

    nominal_non_active = (
            Q(source_choiceset_option__source_attribute__master_attribute__unit__is_active=False)
            | Q(source_choiceset_option__source_attribute__master_attribute__id=None)
            | Q(source_choiceset_option__source_attribute__master_attribute__name='- Checked, Unlinked -')
            | Q(source_choiceset_option__source_attribute__master_attribute__name__exact='')
            | Q(source_entity__master_entity__name__exact='')
            | Q(source_entity__master_entity__id__isnull=True)
            | Q(source_choiceset_option__source_attribute__reference__status=1)
            | Q(source_choiceset_option__source_attribute__reference__status=3)
            | Q(source_choiceset_option__master_choiceset_option__name=None)
    )
    master_attribute_filter = (
        Q(source_choiceset_option__master_choiceset_option__master_attribute_id =
          F('source_choiceset_option__source_attribute__master_attribute__id')
        )
    )

    query = base.exclude(non_active).annotate(
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
        occurrence_id=Case(
            When(occurrence_id__endswith='-0-0-0',then=Value('NA')
            ),
            default='occurrence_id',
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
    ).order_by(
        'source_attribute__master_attribute__name'
    )

    nominal_query = SourceChoiceSetOptionValue.objects.filter(
            master_attribute_filter).exclude(nominal_non_active).annotate(
        trait_id=Concat(
            Value('https://www.mammalbase.net/ma/'),
            'source_choiceset_option__source_attribute__master_attribute__id',
            Value('/'),
            output_field=CharField()
        ),
        trait_value=F('source_choiceset_option__master_choiceset_option__name'),
        verbatim_trait_value=F('source_choiceset_option__name'),
        trait_unit=Value('NA'),
        verbatim_trait_unit=Value('NA'),
        taxon_id=Concat(
            Value('https://www.mammalbase.net/me/'),
            'source_entity__master_entity__id',
            Value('/'),
            output_field=CharField()
        ),
        measurement_id=Concat(
            Value('https://www.mammalbase.net/sav/'),
            'id',
            Value('/'),
            output_field=CharField()
        ),
        occurrence_id=Value('NA'),
        warnings=Value('NA'),
    ).order_by(
        'source_choiceset_option__source_attribute__master_attribute__name'
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

    nominal_fields = [
        ('trait_id', 'traitID'),
        ('source_entity__master_entity__name', 'scientificName'),
        ('source_choiceset_option__source_attribute__master_attribute__name', 'traitName'),
        ('trait_value', 'traitValue'),
        ('trait_unit', 'traitUnit'),
        ('source_entity__name', 'verbatimScientificName'),
        ('source_choiceset_option__source_attribute__name', 'verbatimTraitName'),
        ('verbatim_trait_value', 'verbatimTraitValue'),
        ('verbatim_trait_unit', 'verbatimTraitUnit'),
        ('taxon_id', 'taxonID'),
        ('measurement_id', 'measurementID'),
        ('occurrence_id', 'occurrenceID'),
        ('warnings', 'warnings'),
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
