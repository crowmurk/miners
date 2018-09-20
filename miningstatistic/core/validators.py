import json

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_json(value):
    """Проверяет сохраняемый шаблон
    """
    try:
        if value:
            json.loads(value)
    except ValueError as e:
        raise ValidationError(
            _('%(value)s is not a valid template: %(message)s'),
            params={'value': value, 'message': e, },
        )
