from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import F
from mb.models import SourceLocation, LocationRelation
from .location_api import LocationAPI
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mb.filters import SourceLocationFilter
from .location_match import add_locations
import json

@login_required
#@permission_required('matchtool.trait_match', raise_exception=True)
def trait_match(request):
    #TODO
    return render(request, 'matchtool/trait_match.html')

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
    
    # If the matched locations was added, get the name of it
    if locations and locations[-1] is not None:
        matched_location = locations[-1].name
    else:
        matched_location = None

    # If any  hierarchy locations were added, get the name(s) of them
    if locations and locations[0] is not None:
        hierarchy_locations = [location.name for location in locations[:-1]]
    else:
        hierarchy_locations = []

    return JsonResponse({
        'masterLocation': matched_location,
        'hierarchy_locations': hierarchy_locations
    })