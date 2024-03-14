from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from mb.models import SourceLocation
from .location_api import LocationAPI

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

def location_match_detail(request):
    api = LocationAPI()
    source_location = "Italy"
    result = api.get_master_location(source_location)
    result_locations = result["geonames"]
    result_count = result["totalResultsCount"]

    return render(request, 'matchtool/location_match_detail.html', {'source_location': source_location, 'result_locations': result_locations, 'result_count': result_count})
    