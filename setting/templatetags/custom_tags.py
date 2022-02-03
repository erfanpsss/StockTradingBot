from django import template
import datetime

register = template.Library()

@register.simple_tag
def utc_time_now():
    return datetime.datetime.utcnow()