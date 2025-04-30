from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary by key.
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary and key in dictionary:
        return dictionary[key]
    return None

@register.filter
def get_key(dictionary, key):
    """
    Get an item from a dictionary by key, specifically for date keys in templates.
    Usage: {{ dictionary|get_key:date }}
    """
    for dict_key in dictionary:
        if str(dict_key) == str(key) or dict_key == key:
            return dictionary[dict_key]
    return []