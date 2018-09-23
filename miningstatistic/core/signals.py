from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.utils import get_unique_slug

@receiver(pre_save)
def slug_create(sender, instance, *args, **kwargs):
    """Создает slug при сохранении объекта
    """

    # Аргументы вызова функции создания slug
    args = {
        'Miner': ('slug', 'name', 'version', True),
        'Request': ('slug', 'name', False),
        'Server': ('slug', 'name', True),
    }

    model_name = sender.__name__

    try:
        # Извлекаем аргументы для модели
        slug_field, *slugable_fields, unique = args[model_name]
        # Создаем slug только если он еще не задан
        if instance.slug:
            return None
    except KeyError:
        pass
    else:
        # Создаем slug
        slug = get_unique_slug(
            instance,
            slug_field,
            *slugable_fields,
            unique=unique
        )

        instance.slug = slug
