import difflib
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from mb.models.models import SourceAttribute, AttributeRelation
from django.db.models import Q
import re



@login_required
# @permission_required('matchtool.trait_match', raise_exception=True)
def trait_match(request):
    """Match source attributes to master attributes."""
    unlinked_attributes = SourceAttribute.objects.filter(
        Q(master_attribute=None) | Q(master_attribute__name='- Checked, Unlinked -'))

    relations = AttributeRelation.objects.exclude(
        master_attribute__name='- Checked, Unlinked -')

    for source_attribute in unlinked_attributes:
        matching_relations = relations.filter(
            Q(master_attribute__name=source_attribute.name) |
            Q(source_attribute__name=source_attribute.name) |
            Q(source_attribute__name__contains=source_attribute.name) |
            Q(master_attribute__name__contains=source_attribute.name)
        )
        if matching_relations:
            master_attribute = matching_relations[0].master_attribute
            print(source_attribute.name, master_attribute.name)

        
            
    return render(request, 'matchtool/trait_match.html')


#closest = difflib.get_close_matches(trait, traits, 1, 0.5)  #returns the one best match if the possibility is over 0.5


