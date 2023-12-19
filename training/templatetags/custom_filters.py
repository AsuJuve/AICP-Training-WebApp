# custom_filters.py
from django import template
from math import ceil

register = template.Library()

@register.filter(name='dict_lookup')
def dict_lookup(dictionary, key):
    return dictionary.get(key, None)

@register.filter(name='denormalize_difficulty')
def denormalize_difficulty(normalized):
    denormalized = ceil(normalized * (3500 - 800) + 800)

    return denormalized
