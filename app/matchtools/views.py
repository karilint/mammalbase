from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from mb.models import SourceAttribute, MasterAttribute, AttributeRelation
from django.db.models import Q
from fuzzywuzzy import fuzz, process
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .filters import SourceAttributeFilter

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
        'matchtool/trait_match_list.html',
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

    return "- Checked, Unlinked -"


@login_required
def match_operation_endpoint(request):
    """Handles the AJAX POST request sent when a user tries to make a match."""
    if request.method == "POST":
        source_attribute_id = request.POST.get("source_attribute_id")
        source_attribute = get_object_or_404(
            SourceAttribute, pk=source_attribute_id)
        match = get_match(source_attribute.name)

        try:
            master = MasterAttribute.objects.get(name=match)
            attribute_relation = AttributeRelation.objects.create(
                source_attribute=source_attribute, master_attribute=master
            )
            return JsonResponse({"success": True})
        except MasterAttribute.DoesNotExist:
            return JsonResponse({"success": False, "error": "No matching master attribute found."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method."})