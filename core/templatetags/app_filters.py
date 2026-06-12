from django import template

register = template.Library()

@register.filter
def get_col(columns_dict, key):
    return columns_dict.get(key, [])

@register.filter
def mul(value, arg):
    return value * arg

@register.filter
def pct(value, total):
    if not total:
        return 0
    return round(value / total * 100)
