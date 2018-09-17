from django.utils.text import slugify


def get_unique_slug(instance, slugable_fields, slug_field):
    """ Генерирует уникальный slug.

    Аргументы:
        instance - экземпляр модели
        slugable_fields - строка с именем поля или
            список полей из которых создается slug
        slug_field - строка с именем поля в котором хранится slug.

    Возвращает строку с уникальным slug
    """

    # Если получена строка
    if isinstance(slugable_fields, (bytes, str)):
        slugable_fields = (slugable_fields,)
    # Если получен не итеррируемый тип
    elif not hasattr(slugable_fields, '__iter__'):
        raise TypeError(
            "Sluggable field name must be list "
            "or string, not '{}'".format(
                type(slugable_fields).__name__
            ),
        )

    # Создаем slug
    slug = slugify('-'.join(
        [getattr(instance, slugable_field)
         for slugable_field in slugable_fields]
    ))

    unique_slug = slug
    extension = 1
    ModelClass = instance.__class__

    # Пока slug не будет уникальным
    while ModelClass.object.all().filter(
        slug_field=unique_slug,
    ).exclude(pk=instance.pk).exists():
        # Генерируем новый
        unique_slug = '{}-{}'.format(slug, extension)
        extension += 1

    return unique_slug
