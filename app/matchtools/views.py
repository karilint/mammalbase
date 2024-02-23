import difflib
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required


@login_required
#@permission_required('matchtool.trait_match', raise_exception=True)
def trait_match(request, trait): #trait is the trait that gets matched
    #TODO
    
    closest = difflib.get_close_matches(trait, traits, 1, 0.5)  #returns the one best match if the possibility is over 0.5
    return render(request, 'matchtool/trait_match.html')
