import difflib
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from app.matchtools.models import WordCount
from mb.models.models import SourceAttribute, AttributeRelation
from django.db.models import Q
from fuzzywuzzy import fuzz, process
import time


@login_required
# @permission_required('matchtool.trait_match', raise_exception=True)
def trait_match(request):
    """Match source attributes to master attributes."""
    relations = AttributeRelation.objects.exclude(
        master_attribute__is_active=False
    ).select_related('source_attribute', 'master_attribute').values('source_attribute__name', 'master_attribute__name')

    for source in SourceAttribute.objects.filter(master_attribute=None):
        matches = process.extractOne(source.name, [(item['source_attribute__name'], item['master_attribute__name'])
                                     for item in relations], score_cutoff=80, scorer=fuzz.token_set_ratio)
        
    for attribute in relations: # Tällä käydään läpi olemassaolevat relaatiot ja luodaan sanataulukko
        master = attribute['master_attribute__mane']
        sources = attribute['source_attribute__name'].split(" ")
        for source in sources:
            joku = WordCount.objects.filter(
                Q(word = source)
            )
            if joku != None: 
                WordCount.object.create(
                    word = source,
                    master_attribute = master
                )

        if matches:
            print(source.name, matches[0], matches[1])

    return render(request, 'matchtool/trait_match.html')