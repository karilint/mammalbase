from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.http import JsonResponse
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
    filter = SourceLocationFilter(request.GET, queryset=SourceLocation.objects.is_active().select_related())
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

    return render(request, 'matchtool/source_location_list.html', {'page_obj': page_obj, 'filter': filter})

def location_match_detail(request, id):
    api = LocationAPI()
    sourceLocation = SourceLocation.objects.get(id=id)
    result = api.get_locations(sourceLocation)
    
    query = sourceLocation
    
    if request.method == 'POST':
        query = request.POST.get('query')
        result = api.get_locations(query)

    result_locations = result["geonames"][:10]
    result_count = result["totalResultsCount"]
    id_list = request.session.get('id_list')
    index = id_list.index(id)+1
    previous=id_list.index(id)-1
    next_id = id_list[index] if index < len(id_list) else None
    previous_id = id_list[previous] if previous >= 0 else None
    
    return render(request, 'matchtool/location_match_detail.html', {
        'query': query,
        'sourceLocation': sourceLocation, 
        'result_locations': result_locations, 
        'result_count': result_count, 
        'next_id': next_id, 
        'current_index': index, 
        'id_count': len(id_list), 
        'previous_id': previous_id
    })

def match_location(request):
    api = LocationAPI()
    geo_names_location = request.POST.get('geoNamesLocation')
    source_location_id = request.POST.get('sourceLocation')
    
    geo_names_location = geo_names_location.replace("'", '"')
    geo_names_location = json.loads(geo_names_location)
    
    locations = add_locations(geo_names_location)
    matched_location = locations[0]
    hierarchy_locations = locations[1:]
        
    source_location = SourceLocation.objects.get(id=source_location_id)
    
    LocationRelation(master_location=matched_location, source_location=source_location).save()

    return JsonResponse({'masterLocation': matched_location.name, 'hierarchy_locations': hierarchy_locations})