import django_filters
from mb.models import SourceAttribute, MasterAttribute

class SourceAttributeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Attribute contains')
    reference__citation = django_filters.CharFilter(lookup_expr='icontains', label='Reference contains')
    master_attribute = django_filters.ModelChoiceFilter(queryset=MasterAttribute.objects.filter(is_active=False), label='Master Attribute', empty_label='None')

    class Meta:
        model = SourceAttribute
        fields = ['name', 'reference__citation', 'master_attribute']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not any(self.data.values()):
            self.queryset = SourceAttribute.objects.filter(master_attribute=None)
