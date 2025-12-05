# 2020.02.12 Kari Lintulaakso
# This code is based on a solution provided by 'Reinstate Monica'
# at https://stackoverflow.com/questions/2047622/how-to-paginate-django-with-other-get-variables/57899037#57899037

from urllib.parse import urlencode
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, next_page):
    query = context['request'].GET.copy().urlencode()

    if '&page=' in query:
        url = query.rpartition('&page=')[0] # equivalent to .split('page='), except more efficient
    else:
        url = query
#    return f'{url}&page={next_page}'
    return url+'&page='+str(next_page)
