from django.shortcuts import render
from mb.models import SourceLocation

def location_matchtool(request):
    results = []
    if request.method == 'POST':
        query = request.POST.get('query')
        results = SourceLocation.objects.filter(name=query)
        print(results)
    return render(request, 'location_matchtool.html', {'results': results})