from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from core.utils import get_unique_slug

@receiver(pre_save)
def slug_create(sender, **kwargs):
    """Создает slug при сохранении объекта
    """
    instance = kwargs.get('instance')

    model_name = instance.__class__.__name__

    # Аргументы вызова функции создания slug
    args = {
        'Miner': ('name', 'version', True),
        'Request': ('name', False),
        'Server': ('name', True),
    }

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

        if slug == 'create':
            # Будет совпадение с url создания объекта
            raise ValidationError('Slug may not be ""create".')

        instance.slug = slug
