import json

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def pretty_json(value):
    """Форматирует объект json в виде
    удобном для восприятия
    """
    value = json.loads(value)
    return json.dumps(value, indent=4)
