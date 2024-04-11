from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from mb.models import SourceLocation, LocationRelation
from .location_api import LocationAPI
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mb.filters import SourceLocationFilter
from .location_match import create_master_location, match_locations

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
    
    if request.method == 'POST':
        sourceLocation = request.POST.get('query')
        
    result = api.get_master_location(sourceLocation)
    result_locations = result["geonames"][:10]
    result_count = result["totalResultsCount"]
    id_list = request.session.get('id_list')
    index = id_list.index(id)+1
    previous=id_list.index(id)-1
    next_id = id_list[index] if index < len(id_list) else None
    previous_id = id_list[previous] if previous >= 0 else None
    
    return render(request, 'matchtool/location_match_detail.html', {
        'sourceLocation': sourceLocation, 
        'result_locations': result_locations, 
        'result_count': result_count, 
        'next_id': next_id, 
        'current_index': index, 
        'id_count': len(id_list), 
        'previous_id': previous_id
    })

def match_location(request):
    geoNamesLocation = request.GET.get('geoNamesLocation')
    sourceLocation = request.GET.get('sourceLocation')
    print(geoNamesLocation)
    print(sourceLocation)
    
    #masterLocation = create_master_location(geoNamesLocation)
    masterLocation = "test"
    #match_locations(sourceLocation.id, masterLocation.id)
    
    return render(request, 'matchtool/match_location.html', {'sourceLocation': sourceLocation, 'masterLocation': masterLocation})

    