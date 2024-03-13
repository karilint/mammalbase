from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
# from .models import WordCount
from mb.models import SourceAttribute, MasterAttribute
from django.db.models import Q
from fuzzywuzzy import fuzz, process
import re


@login_required
@permission_required('matchtool.trait_match', raise_exception=True)
def trait_match(request):
    """Match source attributes to master attributes."""
    relations = MasterAttribute.objects.exclude(is_active=False).values_list('name', 'source_attribute__name')

    for source in SourceAttribute.objects.filter(master_attribute=None):
        matches = process.extractOne(source.name, relations, scorer=fuzz.token_set_ratio, score_cutoff=75)
        if matches:
            print(source.name,matches)
            
    # for attribute in relations: # Tällä käydään läpi olemassaolevat relaatiot ja luodaan sanataulukko
    #     master = attribute['master_attribute__name']
    #     sources = attribute['source_attribute__name'].split()
    #     for source in sources:
    #         found_word = WordCount.objects.filter(
    #             Q(word = source) & Q(master_attribute = master)
    #         )
    #         if found_word == None: #jos sanaa ei löydy luodaan uusi solu siihen kohtaan TODO: tee jotain "tyhjille" soluille, kun lasketaan todennäköisyydet
    #             WordCount.object.create(
    #                 word = source,
    #                 master_attribute = master,
    #                 count = 1
    #             )
    #         else: #Jos sana löytyy, lisätään sanojen määrää yhdellä
    #             current_count = found_word['count']
    #             WordCount.objects.filter(
    #             Q(word = source) & Q(master_attribute = master)
    #         ).update(count = current_count + 1)

    return render(request, 'matchtool/trait_match.html')