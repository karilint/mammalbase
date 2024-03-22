from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from mb.models import SourceAttribute, MasterAttribute, AttributeRelation
from django.db.models import Q
from fuzzywuzzy import fuzz, process
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mb.filters import SourceAttributeFilter


@login_required
def trait_match_list(request):
    """List all source attributes and their best match from master attributes."""
    f = SourceAttributeFilter(request.GET, queryset=SourceAttribute.objects.filter(
        Q(master_attribute=None) | Q(master_attribute__is_active=False)))
    master_attributes = MasterAttribute.objects.all()
    paginator = Paginator(f.qs, 10)

    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    for source_attribute in page_obj:
        match = get_match(source_attribute.name)
        if match:
            source_attribute.matched_master = MasterAttribute.objects.get(
                name=match)

    return render(
        request,
        'matchtool/info_trait_match.html',
        {'page_obj': page_obj, 'filter': f, 'master_attributes': master_attributes}
    )


def get_match(source_name):
    """Get best match for source attribute from master attributes and source attributes."""
    relations = MasterAttribute.objects.exclude(
        is_active=False).values_list('name', 'source_attribute__name')

    sources = [rel[1] for rel in relations]
    masters = [rel[0] for rel in relations]

    master_match = process.extractOne(
        source_name, masters, scorer=fuzz.token_set_ratio, score_cutoff=70)
    if master_match:
        return master_match[0]

    source_match = process.extractOne(
        source_name, sources, scorer=fuzz.token_set_ratio, score_cutoff=70)
    if source_match:
        index = sources.index(source_match[0])
        return relations[index][0]

    return None


@login_required
def match_operation_endpoint(request):
    if request.method == "POST":
        source_attribute_id = request.POST.get("source_attribute_id")
        source_attribute = get_object_or_404(
            SourceAttribute, pk=source_attribute_id)
        match = get_match(source_attribute.name)
        if match:
            master = MasterAttribute.objects.get(name=match)
            attribute_relation = AttributeRelation.objects.create(
                source_attribute=source_attribute, master_attribute=master
            )

            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "No match found."})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method."})

# @login_required
# @permission_required('matchtool.trait_match', raise_exception=True)
# def trait_match(request, source_attribute_id):
#     """Match source attributes to master attributes."""
#     unmatched_source = get_object_or_404(
#         SourceAttribute, pk=source_attribute_id)
#     found_match = get_match(unmatched_source.name)
#     if not found_match:
#         return redirect('info-trait-match')

#     master = MasterAttribute.objects.get(name=found_match)
#     attribute_relation = AttributeRelation(
#         source_attribute=unmatched_source, master_attribute=master)
#     form = AttributeRelationForm(instance=attribute_relation)

#     if request.method == 'POST':
#         form = AttributeRelationForm(request.POST, instance=attribute_relation)
#         if form.is_valid():
#             form.save()
#             next_source = get_unmatched()
#             if next_source:
#                 return redirect('trait-match', source_attribute_id=next_source.id)
#             else:
#                 return redirect('info-trait-match')

#     return render(request, 'matchtool/trait_match.html', {'form': form, 'unmatched_source': unmatched_source})


# def get_unmatched():
#     """Get first unmatched source attribute."""
#     for source in SourceAttribute.objects.filter(master_attribute=None):
#         match = get_match(source.name)
#         if match:
#             return source
#     return None

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
