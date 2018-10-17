from django import template

register = template.Library()


@register.filter
def verbose_name(obj):
    """Фильтр получает verbose_name модели
    """
    return getattr(obj._meta, 'verbose_name', '')


@register.filter
def verbose_name_plural(obj):
    """Фильтр получает verbose_name_plural модели
    """
    return getattr(obj._meta, 'verbose_name_plural', '')


@register.simple_tag
def field_verbose_name(obj, field):
    """Тег получает verbose_name поля заданой модели
    """
    field = obj._meta.get_field(field)

    if hasattr(field, 'verbose_name'):
        # Обычное поле или RelationField forward
        return getattr(field, 'verbose_name', '')
    try:
        # RelationField reverce
        related_model_meta = field.related_model._meta
    except AttributeError:
        return ''
    return getattr(related_model_meta, 'verbose_name_plural', '')
