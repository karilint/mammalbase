from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from mb.models import SourceLocation, LocationRelation
from .location_api import LocationAPI
from .location_match import create_master_location, match_locations

@login_required
#@permission_required('matchtool.trait_match', raise_exception=True)
def trait_match(request):
    #TODO
    return render(request, 'matchtool/trait_match.html')

def location_matchtool(request):
    sources = []
    locations = []
    count = 0
    api = LocationAPI()
    if request.method == 'POST':
        query = request.POST.get('query')
        result = api.get_master_location(query)
        locations = result["geonames"]
        count = result["totalResultsCount"]
        sources = SourceLocation.objects.filter(name__icontains=query)
    return render(request, 'matchtool/location_matchtool.html', {'locations': locations, 'count': count, 'sources': sources})

def location_match_detail(request, id):
    api = LocationAPI()
    sourceLocation = SourceLocation.objects.get(id=id)
    
    if request.method == 'POST':
        sourceLocation = request.POST.get('query')
        
    result = api.get_master_location(sourceLocation)
    result_locations = result["geonames"][:10]
    result_count = result["totalResultsCount"]

    return render(request, 'matchtool/location_match_detail.html', {'sourceLocation': sourceLocation, 'result_locations': result_locations, 'result_count': result_count})

def match_location(request):
    geoNamesLocation = request.GET.get('geoNamesLocation')
    sourceLocation = request.GET.get('sourceLocation')
    print(geoNamesLocation)
    print(sourceLocation)
    
    #masterLocation = create_master_location(geoNamesLocation)
    masterLocation = "test"
    #match_locations(sourceLocation.id, masterLocation.id)
    
    return render(request, 'matchtool/match_location.html', {'sourceLocation': sourceLocation, 'masterLocation': masterLocation})

    