import django_filters
from mb.models import SourceAttribute, MasterAttribute, SourceLocation


class SourceAttributeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Attribute contains')

    reference__citation = django_filters.CharFilter(
        field_name='reference__citation',
        label='Reference contains',
        lookup_expr='icontains',
        method='filter_reference'
    )

    master_attribute = django_filters.ModelChoiceFilter(
        queryset=MasterAttribute.objects.filter(name='- Checked, Unlinked -'),
        label='Standard Trait',
        empty_label='None')

    def filter_reference(self, queryset, name, value):
        if value:
            return queryset.filter(reference__citation__icontains=value)
        return queryset

    class Meta:
        model = SourceAttribute
        fields = ['name', 'reference__citation', 'master_attribute']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.data.get('master_attribute'):
            self.queryset = self.queryset.filter(
                master_attribute__name='- Checked, Unlinked -')
        else:
            self.queryset = self.queryset.filter(master_attribute=None)
            
class SourceLocationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Location contains')
    reference__citation = django_filters.CharFilter(lookup_expr='icontains', label='Reference contains')
    match_attempts_gte = django_filters.NumberFilter(field_name='match_attempts', lookup_expr='gte', label='Match attempts')
    match_attempts_lte = django_filters.NumberFilter(field_name='match_attempts', lookup_expr='lte', label='Match attempts to')

    class Meta:
        model = SourceLocation
        fields = ['name', 'reference__citation', 'match_attempts_gte', 'match_attempts_lte']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields['match_attempts_gte'].initial = 0
        self.form.fields['match_attempts_lte'].initial = 0
