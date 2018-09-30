from django.test import TestCase
from django.core.exceptions import ValidationError

from miner.models import Miner, Request, Server
from core.utils import get_unique_slug

# Create your tests here.

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


class GetSlugTest(TestCase):
    """Тестирование гнерератора slug
    """

    def test_get_unique_slug(self):
        """Генерация уникального slug
        """
        # Создаем первый объект
        miner = Miner(name='Miner', version='1.0.b')
        miner.slug = get_unique_slug(
            miner,
            'slug',
            'name', 'version',
        )
        miner.save()

        # Создаем второй объект с таким же slug
        other_miner = Miner(name='MineR', version='1.0.b')
        other_miner.slug = get_unique_slug(
            other_miner,
            'slug',
            'name', 'version',
        )

        # Поля slug не должны совпадать
        self.assertNotEqual(miner.slug, other_miner.slug)

    def test_get_unique_slug_conflict(self):
        """Генерация уникального slug недопустимого значения
        """
        miner = Miner(name='Miner', version='1.0.b')
        miner.save()

        # Создаем объект, чей slug недопустимым
        server = Server(
            name='Create',
            host='192.168.1.1',
            port=80,
            miner=miner,
        )
        server.slug = get_unique_slug(
            server,
            'slug',
            'name',
        )

        # Slug не должен быть недопустимого значения
        self.assertNotEqual(server.slug, 'create')
        server.save()

        # Создаем второй объект, чей slug недопустимым
        other_server = Server(
            name='CreatE',
            host='192.168.1.1',
            port=80,
            miner=miner,
        )
        other_server.slug = get_unique_slug(
            other_server,
            'slug',
            'name',
        )

        # Slug не должен быть недопустимого значения
        self.assertNotEqual(other_server.slug, 'create')

        # Поля slug не должны совпадать
        self.assertNotEqual(server.slug, other_server.slug)

    def test_get_slug(self):
        """Генерация неуникального slug
        """
        # Создаем первый объект
        miner = Miner(name='Miner', version='1.0.b')
        miner.slug = get_unique_slug(
            miner,
            'slug',
            'name', 'version',
            unique=False,
        )
        miner.save()

        # Создаем второй объект с таким же slug
        other_miner = Miner(name='MineR', version='1.0.b')
        other_miner.slug = get_unique_slug(
            other_miner,
            'slug',
            'name', 'version',
            unique=False,
        )

        # Поля slug должны быть равны
        self.assertEqual(miner.slug, other_miner.slug)

    def test_get_slug_conflict(self):
        """Генерация неуникального slug недопустимого значения
        """
        miner = Miner(name='Miner', version='1.0.b')
        miner.save()

        # Создаем объект, чей slug недопустимым
        server = Server(
            name='Create',
            host='192.168.1.1',
            port=80,
            miner=miner,
        )
        server.slug = get_unique_slug(
            server,
            'slug',
            'name',
            unique=False,
        )

        # Slug не должен быть недопустимого значения
        self.assertNotEqual(server.slug, 'create')
        server.save()

        # Создаем второй объект, чей slug недопустимым
        other_server = Server(
            name='CreatE',
            host='192.168.1.1',
            port=80,
            miner=miner,
        )
        other_server.slug = get_unique_slug(
            other_server,
            'slug',
            'name',
            unique=False,
        )

        # Slug не должен быть недопустимого значения
        self.assertNotEqual(other_server.slug, 'create')

        # Поля slug должны быть равны
        self.assertEqual(server.slug, other_server.slug)

    def test_get_unique_together_slug(self):
        """Гнереация уникального slug для поля
        """
        # Slug должен быть уникальным для значения поля miner
        miner = Miner(name='Miner', version='1.0.b')
        miner.save()
        other_miner = Miner(name='OtherMiner', version='1.0.b')
        other_miner.save()

        # Создаем первый объект
        first_request = Request(
            name='Status',
            request='{"a": 1}',
            miner=miner,
        )
        first_request.slug = get_unique_slug(
            first_request,
            'slug',
            'name',
            unique=('miner',),
        )
        first_request.save()

        # Создаем второй объект, с таким же полем miner
        second_request = Request(
            name='Status',
            request='{"a": 1}',
            miner=miner,
        )
        second_request.slug = get_unique_slug(
            second_request,
            'slug',
            'name',
            unique=('miner',),
        )

        # Поля slug не должны совпадать
        self.assertNotEqual(first_request.slug, second_request.slug)
        second_request.save()

        # Создаем третий объект, с другим полем miner
        third_request = Request(
            name='Status',
            request='{"a": 1}',
            miner=other_miner,
        )
        third_request.slug = get_unique_slug(
            third_request,
            'slug',
            'name',
            unique=('miner',),
        )

        # Поля slug должны совпадать
        self.assertEqual(third_request.slug, first_request.slug)
