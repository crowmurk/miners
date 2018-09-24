from django.utils.text import slugify


def get_unique_slug(instance, slug_field, *slugable, unique=True):
    """ Генерирует уникальный slug.

    Аргументы:
        instance - экземпляр модели
        slug_field - строка с именем поля в котором хранится slug
        slugable - источник для создания slug:
            строки для создания slug
            строки с  именами полей экземпляра
            значения для создания slug
        unique - должен ли slug быть уникальным:
            True/False - для всей модели
            field - строка с именем поля с учетом значения
                которого slug должен быть уникальным или
                список строк с именами полей

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

    # Значения slug конфликтуют с url
    conflict = slug in ('create', 'update', 'delete')

    if unique:
        # При необходимости проверям slug на уникальность
        Model = instance.__class__
        extension = 1

        if conflict:
            # Начинаим поиск конфилктов с 'slug-1'
            unique_slug = '{}-{}'.format(slug, extension)
            extension += 1
        else:
            # Начинаим поиск конфилктов с 'slug'
            unique_slug = slug

        # Формируем словарь для фильтрации модели
        filter_dict = {slug_field: unique_slug}

        if not isinstance(unique, bool):
            # Если необходимо учитывать
            # значения других полей, например:
            # unique_together((slug, field, ))
            if isinstance(unique, str):
                # Если поле только одно
                filter_dict.update(
                    {unique: getattr(instance, unique)}
                )
            elif isinstance(unique, (list, tuple, set)):
                # Если передан список полей
                filter_dict.update(
                    {field: getattr(instance, field)
                     for field in unique}
                )
            else:
                raise ValueError(
                    "'unique' argument must be bool,"
                    " str or iterable of str, not {}.".format(
                        type(unique),
                    )
                )

        # Пока slug не будет уникальным
        while Model.objects.filter(
            **filter_dict,
        ).exclude(id=instance.id).exists():
            # Генерируем новый вида
            # slug-1, slug-2,..., slug-n
            unique_slug = '{}-{}'.format(slug, extension)
            filter_dict.update({slug_field: unique_slug})
            extension += 1

        return unique_slug

    return "{}-{}".format(slug, 1) if conflict else slug
