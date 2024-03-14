from django.shortcuts import render
from mb.models import SourceLocation
from .location_api import LocationAPI

def location_matchtool(request):
    result = []
    sources = []
    api = LocationAPI()
    if request.method == 'POST':
        query = request.POST.get('query')
        result = api.get_master_location(query)
        locations = result["geonames"]
        count = result["totalResultsCount"]
        sources = SourceLocation.objects.filter(name__icontains=query)
    return render(request, 'location_matchtool.html', {'locations': locations, 'count': count, 'sources': sources})