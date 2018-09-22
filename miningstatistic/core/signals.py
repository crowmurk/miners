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

        if slug == 'create' or (
                model_name == 'Request' and slug in (
                    'update',
                    'delete',
                )):
            # Будет совпадение с url представлений объекта
            raise ValidationError(
                'Slug may not be "{slug}" for object "{model}".'
                'Try to change following fields: "{fields}":'.format(
                    slug=slug,
                    model=model_name,
                    fields=', '.join(field for field in slugify),
                ),
            )

        instance.slug = slug
