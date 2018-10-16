from django.db import models
from django.urls import reverse
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    validate_ipv46_address
)

from core.validators import validate_json, validate_slug

# Create your models here.

class Miner(models.Model):
    name = models.CharField(
        max_length=31,
        verbose_name='Майнер',
    )
    version = models.CharField(
        max_length=31,
        verbose_name='Версия',
    )
    slug = models.SlugField(
        max_length=63,
        unique=True,
        editable=False,
        validators=[
            validate_slug,
        ],
        help_text='URL идентификатор объекта',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Описание',
    )

    class Meta:
        verbose_name = 'Майнер'
        verbose_name_plural = 'Майнеры'
        ordering = ['name', 'version']
        unique_together = (('name', 'version'),)

    def __str__(self):
        return "{name} {version}".format(
            name=self.name,
            version=self.version,
        )

    def get_absolute_url(self):
        return reverse(
            'miner:miner:detail',
            kwargs={'slug': self.slug},
        )

    def get_update_url(self):
        return reverse(
            'miner:miner:update',
            kwargs={'slug': self.slug},
        )

    def get_delete_url(self):
        return reverse(
            'miner:miner:delete',
            kwargs={'slug': self.slug},
        )

    def get_request_create_url(self):
        return reverse(
            'miner:miner:request:create',
            kwargs={'miner_slug': self.slug})


class Request(models.Model):
    name = models.CharField(
        max_length=31,
        verbose_name='Имя',
    )
    slug = models.SlugField(
        max_length=31,
        editable=False,
        validators=[
            validate_slug,
        ],
        help_text='URL идентификатор объекта',
    )
    request = models.TextField(
        max_length=255,
        validators=[
            validate_json,
        ],
        verbose_name='Запрос',
    )
    response = models.TextField(
        blank=True,
        validators=[
            validate_json,
        ],
        verbose_name='Ответ',
        help_text='Шаблон проверки ответа',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Описание',
    )
    miner = models.ForeignKey(
        Miner,
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name='Майнер',
    )

    class Meta:
        verbose_name = 'Запрос'
        verbose_name_plural = 'Запросы'
        ordering = ['miner', 'name']
        unique_together = (('miner', 'slug'),)

    def __str__(self):
        return "{miner} - {name}".format(
            miner=self.miner,
            name=self.name,
        )

    def get_absolute_url(self):
        return reverse(
            'miner:miner:request:detail',
            kwargs={
                'request_slug': self.slug,
                'miner_slug': self.miner.slug,
            },
        )

    def get_update_url(self):
        return reverse(
            'miner:miner:request:update',
            kwargs={
                'request_slug': self.slug,
                'miner_slug': self.miner.slug,
            },
        )

    def get_delete_url(self):
        return reverse(
            'miner:miner:request:delete',
            kwargs={
                'request_slug': self.slug,
                'miner_slug': self.miner.slug,
            },
        )


class Server(models.Model):
    name = models.CharField(
        max_length=31,
        unique=True,
        verbose_name='Имя',
    )
    slug = models.SlugField(
        max_length=31,
        unique=True,
        editable=False,
        validators=[
            validate_slug,
        ],
        help_text='URL идентификатор объекта',
    )
    host = models.GenericIPAddressField(
        validators=[
            validate_ipv46_address,
        ],
        verbose_name='Адрес',
    )
    miner = models.ForeignKey(
        Miner,
        on_delete=models.CASCADE,
        related_name='servers',
        verbose_name='Майнер',
    )
    port = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(65535),
        ],
        verbose_name='Порт',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Описание',
    )

    class Meta:
        verbose_name = 'Сервер'
        verbose_name_plural = 'Серверы'
        ordering = ['name']

    def __str__(self):
        return "{name} - {host}:{port} ({miner})".format(
            name=self.name,
            host=self.host,
            port=self.port,
            miner=self.miner,
        )

    def get_absolute_url(self):
        return reverse(
            'miner:server:detail',
            kwargs={'slug': self.slug},
        )

    def get_update_url(self):
        return reverse(
            'miner:server:update',
            kwargs={'slug': self.slug},
        )

    def get_delete_url(self):
        return reverse(
            'miner:server:delete',
            kwargs={'slug': self.slug},
        )
