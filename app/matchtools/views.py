from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
#from .models import WordCount
from .forms import AttributeRelationForm
from mb.models import SourceAttribute, MasterAttribute
from django.db.models import Q
from fuzzywuzzy import fuzz, process

@login_required
def info_traitmatch(request):
    """Match tool info page."""
    return render(request, 'matchtool/info_trait_match.html')

@login_required 
@permission_required('matchtool.trait_match', raise_exception=True)
def trait_match(request):
    """Match source attributes to master attributes."""
    relations = MasterAttribute.objects.exclude(is_active=False).values_list('name', 'source_attribute__name')[:20]

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

    unmatched_source = SourceAttribute.objects.filter(master_attribute=None).first()
    form = AttributeRelationForm(instance=unmatched_source)

    if request.method == "POST":
        form = AttributeRelationForm(request.POST, instance=unmatched_source)
        if form.is_valid():
            form.save()
            # Optionally mark the source trait as matched
            unmatched_source.matched = True
            unmatched_source.save()
            return HttpResponseRedirect('/matchtools/tm/')  # Redirect to get the next unmatched source trait
        else:
            form = AttributeRelationForm(instance=unmatched_source)

    return render(request, 'matchtool/trait_match.html', {'form': form, 'unmatched_source': unmatched_source})
