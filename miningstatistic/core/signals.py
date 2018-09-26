from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.utils import get_unique_slug


@receiver(pre_save)
def slug_create(sender, instance, *args, **kwargs):
    """Создает slug при сохранении объекта в БД
    """

    # Создаем slug только если он еще не задан
    if instance.slug:
        return None

    # Аргументы вызова функции создания slug
    args = {
        'miner': {
            'Miner': ('slug', 'name', 'version', True),
            'Request': ('slug', 'name', ('miner', )),
            'Server': ('slug', 'name', True),
        },
        'task': {
            'Config': ('slug', 'name', True),
        },
    }

    model_name = sender.__name__
    instance_app = instance._meta.app_label

    try:
        # Извлекаем аргументы для модели
        slug_field, *slugable_fields, unique = args[instance_app][model_name]
    except KeyError:
        return None
    else:
        # Создаем slug
        slug = get_unique_slug(
            instance,
            slug_field,
            *slugable_fields,
            unique=unique
        )

        instance.slug = slug
