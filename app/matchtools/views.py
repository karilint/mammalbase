from pathlib import WindowsPath

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied
from fuzzywuzzy import fuzz, process

from .filters import SourceAttributeFilter
from mb.views import user_is_data_admin_or_contributor
from mb.models import SourceAttribute, MasterAttribute, AttributeRelation


@login_required
def trait_match_list(request):
    """List all source attributes and their best match from master attributes."""
    if not user_is_data_admin_or_contributor(request.user):
        raise PermissionDenied
    
    f = SourceAttributeFilter(request.GET, queryset=SourceAttribute.objects.annotate(
        num_master_attributes=Count('master_attribute')
    ).filter(Q(num_master_attributes=0) | (Q(num_master_attributes=1) & Q(master_attribute__is_active=False))))

    master_attributes = MasterAttribute.objects.all()
    paginator = Paginator(f.qs.order_by('name'), 10)

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
    print("tänne päästiin")
    print(source_name)
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
    """Handles the AJAX POST request sent when a user tries to make a match."""
    if request.method == "POST":
        source_attribute_id = request.POST.get("source_attribute_id")
        selected_master_attribute_id = request.POST.get("selected_master_attribute_id")

        selected_master_attribute = get_object_or_404(MasterAttribute, pk=selected_master_attribute_id)
        source_attribute = get_object_or_404(SourceAttribute, pk=source_attribute_id)
        attribute_relation = AttributeRelation.objects.create(
            source_attribute=source_attribute, master_attribute=selected_master_attribute
        )
        
        messages.success(request, "Match successful!")
        return JsonResponse({"success": True})
    else:
        messages.error(request, "Invalid request method.")
        return JsonResponse({"success": False, "error": "Invalid request method."})
    
@login_required
def source_attribute_edit(request):
    print("kyllä täällä ollaan")
    if request.method == "POST":
        source_attribute_id = request.POST.get("source_attribute_id")
        new_name = request.POST.get("new_name")

        response_data = {}

        # Assuming the source attribute ID is unique to identify the table row
        response_data['source_attribute_id'] = source_attribute_id
        response_data['new_name'] = new_name
        print(response_data)
        return JsonResponse(response_data)
    else:
        messages.error(request, "Invalid request method.")
        return JsonResponse({"success": False, "error": "Invalid request method."})