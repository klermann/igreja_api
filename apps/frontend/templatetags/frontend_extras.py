from django import template

register = template.Library()

@register.filter
def attr(obj, name: str):
    try:
        return getattr(obj, name)
    except Exception:
        return ""
