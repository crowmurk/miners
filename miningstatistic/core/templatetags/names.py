from django import template

register = template.Library()


@register.filter
def verbose_name(obj):
    """Получает verbose_name модели
    """
    return getattr(obj._meta, 'verbose_name', '')


@register.filter
def verbose_name_plural(obj):
    """Получает verbose_name_plural модели
    """
    return getattr(obj._meta, 'verbose_name_plural', '')


@register.simple_tag
def field_verbose_name(obj, field):
    """Тег получает verbose_name
    поля заданой модели
    """
    return getattr(obj._meta.get_field(field), 'verbose_name', '')
