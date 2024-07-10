import datetime
from django import template
from django.conf import settings

register = template.Library()


# settings value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@register.filter(name="unix_to_datetime")
def unix_to_datetime(value):
    return datetime.datetime.fromtimestamp(int(value))
