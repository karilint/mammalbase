import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from fuzzywuzzy import fuzz, process
from mb.models import (AttributeRelation, LocationRelation, MasterAttribute,
                       SourceAttribute, SourceLocation)
from mb.views import user_is_data_admin_or_contributor

from .filters import SourceAttributeFilter, SourceLocationFilter
from .location_api import LocationAPI
from .location_match import add_locations, get_hierarchy_chain


@login_required
def trait_match_list(request):
    """List all source attributes and their best match from master attributes."""
    if not user_is_data_admin_or_contributor(request.user):
        raise PermissionDenied

    reference_citation = request.GET.get('reference_citation')

    f = SourceAttributeFilter(
        request.GET,
        queryset=SourceAttribute.objects.annotate(
            num_master_attributes=Count('master_attribute')
        ).filter(
            Q(num_master_attributes=0) |
            (Q(num_master_attributes=1) & Q(master_attribute__is_active=False))
        ),
    )

    if reference_citation:
        f.filters['reference__citation'].extra['initial'] = reference_citation

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
        source_attribute_id = request.POST.get('source_attribute_id')
        selected_master_attribute_id = request.POST.get(
            'selected_master_attribute_id')

        selected_master_attribute = get_object_or_404(
            MasterAttribute, pk=selected_master_attribute_id)
        source_attribute = get_object_or_404(
            SourceAttribute, pk=source_attribute_id)
        AttributeRelation.objects.create(
            source_attribute=source_attribute, master_attribute=selected_master_attribute
        )

        messages.success(request, "Match successful!")
        return JsonResponse({"success": True})
    messages.error(request, "Invalid request method.")
    return JsonResponse({"success": False, "error": "Invalid request method."})

@login_required
def new_match_endpoint(request):
    """Handles the AJAX POST request sent when a user tries to make a new match."""
    if request.method == "POST":
        source_attribute_name = request.POST.get("source_attribute_name")
        match = get_match(source_attribute_name)
        if match:
            matched_master_attribute = MasterAttribute.objects.get(name=match)
            return JsonResponse({"match": {"id": matched_master_attribute.id}})
        return JsonResponse({"match": None})
    return JsonResponse({"error": "Invalid request method."})

@login_required
def source_location_list(request):
    """List all source locations to be matched with master locations"""
    filter = SourceLocationFilter(
        request.GET,
        queryset=SourceLocation.objects
        .is_active().select_related()
        .exclude(locationrelation__isnull=False)
    )
    id_list = [x.id for x in filter.qs]
    paginator = Paginator(filter.qs, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    request.session['id_list'] = id_list

    return render(request, 'matchtool/source_location_list.html', {
        'page_obj': page_obj,
        'filter': filter
    })

def location_match_detail(request, id):
    """View for single source locations match page"""
    api = LocationAPI()
    source_location = SourceLocation.objects.get(id=id)

    # Increment the match_attempts field of the source location
    SourceLocation.objects.filter(id=id).update(match_attempts=F('match_attempts') + 1)

    result = api.get_locations(source_location)

    # Set the initial query and selected_option
    query = source_location
    selected_option = 'all'

    # If the request method is POST, update the query and selected_option
    # and get the locations or nature reserves from the GeoNames API
    if request.method == 'POST':
        selected_option = request.POST.get('limit_search')
        query = request.POST.get('query')
        if selected_option == 'all':
            result = api.get_locations(query)
        elif selected_option == 'reserves':
            reserves = api.get_nature_reserves(query)
            result = {
                "geonames": reserves,
                "totalResultsCount": len(reserves)
            }

    result_locations = result["geonames"][:10]
    id_list = request.session.get('id_list')

    # Get the current, previous and next ids of the locations to be matched
    index = id_list.index(id)+1
    previous=id_list.index(id)-1
    next_id = id_list[index] if index < len(id_list) else None
    previous_id = id_list[previous] if previous >= 0 else None

    # Check if the source location is already matched
    matched = LocationRelation.objects.filter(source_location=source_location).exists()

    return render(request, 'matchtool/location_match_detail.html', {
        'query': query,
        'sourceLocation': source_location, 
        'result_locations': result_locations,  
        'next_id': next_id, 
        'current_index': index, 
        'id_count': len(id_list), 
        'previous_id': previous_id,
        'selected_option': selected_option,
        'matched': matched,
    })

def match_location(request):
    """Creates a master location and matches it to a source location"""
    geo_names_location = request.POST.get('geoNamesLocation')
    source_location_id = request.POST.get('sourceLocation')

    # Format and parse the GeoNames location as JSON
    geo_names_location = geo_names_location.replace("'", '"')
    geo_names_location = json.loads(geo_names_location)

    # Add the master location and its hierarchy location(s) to the database
    locations = add_locations(geo_names_location, source_location_id)

    final_location = locations[-1] if locations else None

    if final_location is not None:
        matched_location = final_location.name
        hierarchy_locations = get_hierarchy_chain(final_location)
    else:
        matched_location = None
        hierarchy_locations = []

    return JsonResponse({
        'masterLocation': matched_location,
        'hierarchy_locations': hierarchy_locations
    })