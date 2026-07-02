import jdatetime

from django import template

register = template.Library()


@register.filter
def shamsi_date(value):
    if not value:
        return ""
    try:
        date = jdatetime.date.fromgregorian(date=value)
        return date.strftime("%Y/%m/%d")
    except Exception:
        return value


@register.filter
def shamsi_weekday(value):
    if not value:
        return ""
    try:
        # Map Python weekday (Monday=0) to Persian weekday names
        # Monday=0 -> دوشنبه, Tuesday=1 -> سه‌شنبه, ..., Saturday=5 -> شنبه, Sunday=6 -> یک‌شنبه
        greg_weekday = value.weekday() if hasattr(value, "weekday") else None
        persian = [
            "دوشنبه",
            "سه‌شنبه",
            "چهارشنبه",
            "پنج‌شنبه",
            "جمعه",
            "شنبه",
            "یک‌شنبه",
        ]
        if greg_weekday is not None and 0 <= greg_weekday < 7:
            return persian[greg_weekday]
        # fallback: try via jdatetime
        date = jdatetime.date.fromgregorian(date=value)
        return date.strftime("%A")
    except Exception:
        return value
