from django.db.models import Subquery, OuterRef, F, Q
from mb.models import SourceMeasurementValue
from mb.models import UnitConversion


def base_query(measurement_choices):
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
        minplusmax=(F('minimum')*F('coefficient'))+(F('maximum')*F('coefficient'))
    ).exclude(
        Q(source_attribute__master_attribute__name='- Checked, Unlinked -')
        | Q(minplusmax=0)
        | Q(source_attribute__master_attribute__name__exact='')
        | Q(source_entity__master_entity__name__exact='')
        | Q(source_entity__master_entity__id__isnull=True)
    ).filter(measurement_choice_filter)

    return query_filter

