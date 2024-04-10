import django_filters
from mb.models import SourceAttribute, MasterAttribute, SourceReference

class SourceAttributeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Attribute contains')
    reference__citation = django_filters.CharFilter(
        field_name='reference__citation',
        label='Reference',
        lookup_expr='icontains',
        method='filter_reference'
    )
    master_attribute = django_filters.ModelChoiceFilter(
        queryset=MasterAttribute.objects.filter(name='- Checked, Unlinked -'),
        label='Master Attribute',
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
        if not any(key != 'page' and value for key, value in self.data.items()):
            self.queryset = self.queryset.filter(master_attribute=None)
