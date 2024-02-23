from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

@login_required
#@permission_required('matchtool.trait_match', raise_exception=True)
def trait_match(request):
    #TODO
    return render(request, 'matchtool/trait_match.html')
