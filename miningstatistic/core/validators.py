import json

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible

def validate_json(value):
    """Проверяет сохраняемый шаблон
    """
    try:
        if value:
            json.loads(value)
    except ValueError as e:
        raise ValidationError(
            _('%(value)s is not a valid template: %(message)s'),
            code='invalid',
            params={'value': value, 'message': e, },
        )

@deconstructible
class ValidateSlug():
    message = 'Slug не должен быть "%(slug)s" для объекта "%(model)s".'\
        ' попробуйте изменить следующие поля: "%(fields)s"'
    code = 'invalid'

    def __init__(self, model_name, *slugify_fields, message=None, code=None):
        """Принимает:
        model_name: имя модели
        *slugify_fields: список полей из которых создается slug
        message: текст сообщения об ошибке
        code: код ошибки
        """
        self.model_name = model_name
        self.slugify_fields = slugify_fields
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        """Проверяет slug на допустимые значения
        """
        if value.lower() == 'create' or (
                self.model_name == 'Request' and value.lower() in (
                    'update',
                    'delete',
                )
        ):
            # Будет совпадение с url представлений объекта
            raise ValidationError(
                _(self.message),
                code=self.code,
                params={
                    'slug': value,
                    'model': self.model_name,
                    'fields': ', '.join(field for field in self.slugify_fields),
                },
            )

    def __eq__(self, other):
        return (
            isinstance(other, ValidateSlug) and
            (self.model_name == other.model_name) and
            (self.slugify_fields == other.slugify_fields) and
            (self.message == other.message) and
            (self.code == other.code)
        )
