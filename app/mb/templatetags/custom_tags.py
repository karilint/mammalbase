# 2022.04.18 Kari Lintulaakso
# https://www.pluralsight.com/guides/create-custom-template-tags-and-filters-in-django
# https://www.abidibo.net/blog/2014/05/22/check-if-user-belongs-group-django-templates/
# https://gist.github.com/arthuralvim/78129975b31d457fffc6

from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='is_data_admin_or_contributor')
def is_data_admin_or_contributor(user):
    """Return True if the user belongs to the data_admin or
    data_contributor group."""
    if user.groups.filter(name='data_admin').exists():
        return True

    if user.groups.filter(name='data_contributor').exists():
        return True

    return False

@register.filter(name='is_data_admin_or_owner')
def is_data_admin_or_owner(user, data):
    if user.groups.filter(name='data_admin').exists():
        return True

    if user.groups.filter(name='data_contributor').exists() and data.created_by == user:
        return True

    return False

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

@register.filter(name="trim_gender")
def trim_gender(value):
    return value.replace("Gender -", "")

@register.filter(name="trim_lifestage")
def trim_lifestage(value):
    return value.replace("LifeStage -", "")
