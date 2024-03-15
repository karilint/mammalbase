from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
#from .models import WordCount
from .forms import AttributeRelationForm
from mb.models import SourceAttribute, MasterAttribute, AttributeRelation
from django.db.models import Q
from fuzzywuzzy import fuzz, process


@login_required
def info_traitmatch(request):
    """Match tool info page."""
    unmatched_source = get_unmatched()
    return render(request, 'matchtool/info_trait_match.html', {'unmatched_source': unmatched_source})

@login_required
@permission_required('matchtool.trait_match', raise_exception=True)
def trait_match(request, source_attribute_id):
    """Match source attributes to master attributes."""
    unmatched_source = get_object_or_404(
        SourceAttribute, pk=source_attribute_id)
    found_match = get_match(unmatched_source.name)
    if not found_match:
        return redirect('info-trait-match')

    master = MasterAttribute.objects.get(name=found_match)
    attribute_relation = AttributeRelation(
        source_attribute=unmatched_source, master_attribute=master)
    form = AttributeRelationForm(instance=attribute_relation)

    if request.method == 'POST':
        form = AttributeRelationForm(request.POST, instance=attribute_relation)
        if form.is_valid():
            form.save()
            next_source = get_unmatched()
            if next_source:
                return redirect('trait-match', source_attribute_id=next_source.id)
            else:
                return redirect('info-trait-match')

    return render(request, 'matchtool/trait_match.html', {'form': form, 'unmatched_source': unmatched_source})


def get_unmatched():
    """Get first unmatched source attribute."""
    for source in SourceAttribute.objects.filter(master_attribute=None):
        match = get_match(source.name)
        if match:
            return source
    return None


def get_match(source_name):
    """Get best match for source attribute from master attributes using fuzzy matching."""
    relations = MasterAttribute.objects.exclude(
        is_active=False).values_list('name', 'source_attribute__name')
    match = process.extractOne(
        source_name, relations, scorer=fuzz.token_set_ratio, score_cutoff=75)
    return match[0][0] if match else None

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
