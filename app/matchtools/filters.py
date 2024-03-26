import django_filters
from mb.models import SourceAttribute, MasterAttribute
from django.db.models import Q

class SourceAttributeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Attribute contains')
    reference__citation = django_filters.CharFilter(lookup_expr='icontains', label='Reference contains')
    master_attribute = django_filters.ModelChoiceFilter(queryset=MasterAttribute.objects.filter(is_active=False), label='Master Attribute')

    class Meta:
        model = SourceAttribute
        fields = ['name', 'reference__citation', 'master_attribute']

