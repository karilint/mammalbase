from django.db.models import Subquery, OuterRef, F, Q
from mb.models import SourceMeasurementValue
from mb.models import UnitConversion


test_chosen = ['Standard measurements', 'Cranial measurements']
test_list = [Q(source_attribute__master_attribute__attributegrouprelation__group__name=value) for value in test_chosen]
test_filter = Q()
for q in test_list:
    test_filter |= q

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
    Q(source_attribute__master_attribute__name='- Checked, Unlinked -')
    | Q(minplusmax=0)
    | Q(source_attribute__master_attribute__name__exact='')
    | Q(source_entity__master_entity__name__exact='')
    | Q(source_entity__master_entity__id__isnull=True)
)
#.filter(test_filter)
