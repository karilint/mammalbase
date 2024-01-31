from django.db.models import Subquery, OuterRef, F, Q, Case, When, CharField, Value
from django.db.models.functions import Concat
from mb.models.models import SourceMeasurementValue
from mb.models.models import UnitConversion


def base_query(measurement_choices):
    """
        Base query function that the other query sets utilize. Uses the SourceMeasurementValue
        objects to access the model fields.
        Filters necessary to more than one query are also addressed here.
        Occurence_id used in the occurrence_query and traitdata_query is created here.
        Returns the QuerySet.
    """
    non_active = (
              Q(source_attribute__master_attribute__groups__is_active=False)
            | Q(source_attribute__is_active=False)
            | Q(source_attribute__master_attribute__is_active=False)
            | Q(source_entity__is_active=False)
            | Q(source_entity__master_entity__is_active=False)
            | Q(source_unit__is_active=False)
            | Q(source_unit__master_unit__is_active=False)
    ) #filtteröi onko tiettyjen kysymysten arvot active vai non-active

    #  measurement_choices is a list of user choices made in forms.py/views.py.  
    query_filter_list = [Q(source_attribute__master_attribute__attributegrouprelation__group__name=value) for value in measurement_choices]
    measurement_choice_filter = Q()
    for query_filter in query_filter_list:
        measurement_choice_filter |= query_filter

    query_filter = SourceMeasurementValue.objects.annotate(
        coefficient=Subquery(
            UnitConversion.objects.filter(
                from_unit_id=OuterRef('source_unit__master_unit__id'),
                to_unit_id=OuterRef('source_attribute__master_attribute__unit')
            ).values_list('coefficient')[:1]
        )
    ).annotate(
        minplusmax=(F('minimum')*F('coefficient'))+(F('maximum')*F('coefficient')),
        occurrence_id=Concat(
        Case(When(source_entity__id__iexact=None, then=Value('0')),
            default='source_entity__id',
            output_field=CharField()),
            Value('-'),
            Case(When(source_location__id__iexact=None, then=Value('0')),
            default='source_location__id',
            output_field=CharField()),
            Value('-'),
            Case(When(gender__id__iexact=None, then=Value('0')),
            default='gender__id',
            output_field=CharField()),
            Value('-'),
            Case(When(life_stage__id__iexact=None, then=Value('0')),
            default='life_stage__id',
            output_field=CharField())
        )
    ).exclude(non_active).exclude(
        Q(source_attribute__master_attribute__name='- Checked, Unlinked -')
        | Q(minplusmax=0)
        | Q(source_attribute__master_attribute__name__exact='')
        | Q(source_entity__master_entity__name__exact='')
        | Q(source_entity__master_entity__id__isnull=True)
        | Q(source_attribute__reference__status=1)
        | Q(source_attribute__reference__status=3)
    ).filter(measurement_choice_filter)

    return query_filter