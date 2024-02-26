from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from mb.models.models import SourceAttribute, AttributeRelation
from django.db.models import Q

@login_required
# @permission_required('matchtool.trait_match', raise_exception=True)
def trait_match(request):
    """Match source attributes to master attributes."""
    unlinked_attributes = SourceAttribute.objects.filter(
        Q(master_attribute=None) | Q(master_attribute__name='- Checked, Unlinked -'))

    relations = AttributeRelation.objects.exclude(
        master_attribute__name='- Checked, Unlinked -')

    for source_attribute in unlinked_attributes:
        master_attribute = find_exact_match(source_attribute, relations)
        if master_attribute:
            print(source_attribute.name, master_attribute.name)

    return render(request, 'matchtool/trait_match.html')


def find_exact_match(source, relations):
    """Check if source attribute has an exact match in the relations."""
    for relation in relations:
        if source.name.lower() == relation.source_attribute.name.lower():
            return relation.master_attribute
