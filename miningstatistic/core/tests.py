from django.test import TestCase
from django.core.exceptions import ValidationError

from miner.models import Miner, Request

# Create your tests here.

class JsonValidatorTest(TestCase):
    """Тестирование валидатора json
    """

    def test_validate_invalid_json(self):
        """Проверка invalid json
        """
        # Создаем майнер
        miner = Miner.objects.create(
            name='Some Miner',
            version='1.0.0',
        )

        with self.assertRaises(ValidationError):
            # Создаем запрос
            request = Request(
                name='Some Request',
                request='invalid json',
                miner=miner,
            )
            # На этом этапе срабатывают валидаторы
            request.full_clean()
            request.save()

    def test_validate_valid_json(self):
        """Проверка valid json
        """
        # Создаем майнер
        miner = Miner.objects.create(
            name='Some Miner',
            version='1.0.0',
        )

        # Создаем запрос
        request = Request(
            name='Some Request',
            request='{"a": 1}',
            miner=miner,
        )
        # На этом этапе срабатывают валидаторы
        request.full_clean()
        request.save()


class SlugValidatorTest(TestCase):
    """Тестирование валидатора slug
    """

    def test_validate_invalid_slug(self):
        """Проверка invalid slug
        """
        with self.assertRaises(ValidationError):
            # Создаем объект
            miner = Miner(
                name='Some Miner',
                version='1.0.0',
                slug='create',
            )
            # На этом этапе срабатывают валидаторы
            miner.full_clean()
            miner.save()

    def test_validate_valid_slug(self):
        """Проверка valid slug
        """
        # Создаем объект
        miner = Miner(
            name='Some Miner',
            version='1.0.0',
            slug='some-miner-slug',
        )
        # На этом этапе срабатывают валидаторы
        miner.full_clean()
        miner.save()
