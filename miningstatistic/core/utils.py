from django.utils.text import slugify


def get_unique_slug(instance, slug_field, *slugable, unique=True):
    """ Генерирует уникальный slug.

    Аргументы:
        instance - экземпляр модели
        slug_field - строка с именем поля в котором хранится slug
        slugable - источник для создания slug:
            строки для создания slug
            строки с  именами полей экземпляра
            значения полей экземпляра
        unique - должен ли slug быть уникальным

    Возвращает строку с уникальным slug
    """

    # Получаем значения полей экземпляра
    slugable = [
        getattr(instance, field, field)
        if isinstance(field, str)
        else str(field) for field in slugable
    ]

    # Создаем slug
    slug = slugify('-'.join(slugable))

    if unique:
        unique_slug = slug
        extension = 1
        Model = instance.__class__

        # Пока slug не будет уникальным
        while Model.objects.filter(
            **{slug_field: unique_slug},
        ).exclude(id=instance.id).exists():
            # Генерируем новый
            unique_slug = '{}-{}'.format(slug, extension)
            extension += 1
        return unique_slug

    return slug
