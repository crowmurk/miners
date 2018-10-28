import json

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_json(value):
    """Проверяет текстовое поле
    на соответствие формату json
    """
    try:
        if value:
            json.loads(value)
    except ValueError as e:
        raise ValidationError(
            _('An error was founded in %(value)s template: %(message)s'),
            code='invalid',
            params={'value': value, 'message': e, },
        )


def validate_slug(value):
    """Проверяет поле slug на допустимые значения
    """
    if value.lower() in ('create', 'update', 'delete'):
        # Будет совпадение с url представлений объекта
        raise ValidationError(
            _('Slug must not be "%(slug)s"'),
            code='invalid',
            params={'slug': value, },
        )
