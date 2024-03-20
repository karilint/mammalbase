from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from mb.models import SourceLocation
from .location_api import LocationAPI
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mb.filters import SourceLocationFilter

@login_required
#@permission_required('matchtool.trait_match', raise_exception=True)
def trait_match(request):
    #TODO
    return render(request, 'matchtool/trait_match.html')

@login_required
def source_location_list(request):
    """List all source locations to be matched with master locations"""
    filter = SourceLocationFilter(request.GET, queryset=SourceLocation.objects.is_active().select_related())
    paginator = Paginator(filter.qs, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'matchtool/source_location_list.html', {'page_obj': page_obj, 'filter': filter})