from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.utils import get_unique_slug

@receiver(pre_save)
def slug_create(sender, **kwargs):
    """Создает slug при сохранении объекта
    """
    instance = kwargs.get('instance')

    # Аргументы вызова функции создания slug
    args = {
        'Miner': ('name', 'version', True),
        'Request': ('name', False),
        'Server': ('name', True),
    }

    model_name = instance.__class__.__name__

    if model_name in args and instance.slug:
        return

    try:
        # Извлекаем аргументы для модели
        *slugify, unique = args[model_name]
    except KeyError:
        pass
    else:
        # Создаем slug
        slug = get_unique_slug(
            instance,
            'slug',
            *slugify,
            unique=unique
        )

        if slug == 'create' or (
                model_name == 'Request' and slug in (
                    'update',
                    'delete',
                )
        ):
            instance.slug = slug + '_'
        else:
            instance.slug = slug

        # Проверяем поля
        instance.clean_fields()
