from django import template

register = template.Library()


@register.filter
def currency(value):
    try:
        # format with thousands separator and append unit
        return f"{int(value):,} تومان"
    except Exception:
        return value
