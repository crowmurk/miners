from django.db import models
from django.urls import reverse
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    validate_ipv46_address,
    RegexValidator,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from miner.models import Server, Request

from core.validators import validate_slug

# Create your models here.

class Config(models.Model):
    NOLOG = 'NO'
    SYSTEM = 'SY'
    STDOUT = 'ST'
    FILE = 'FI'

    LOG_CHOICES = (
        (NOLOG, 'Выключить'),
        (SYSTEM, 'Системный журнал'),
        (STDOUT, 'Консоль'),
        (FILE, 'Файл'),
    )

    name = models.CharField(
        max_length=31,
        unique=True,
        verbose_name='Имя',
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
    enabled = models.BooleanField(
        default=False,
        verbose_name='Активна',
    )
    refresh = models.PositiveSmallIntegerField(
        default=30,
        validators=[
            MinValueValidator(10),
        ],
        verbose_name='Интервал опроса серверов',
        help_text='Интервал опроса серверов (сек.).',
    )
    zabbix_server = models.GenericIPAddressField(
        blank=True,
        null=True,
        validators=[
            validate_ipv46_address,
        ],
        verbose_name='Адрес Zabbix сервера',
    )
    zabbix_port = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(65535),
        ],
        verbose_name='Порт Zabbix сервера',
    )
    zabbix_timeout = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(60),
        ],
        verbose_name='Таймаут Zabbix сервера',
    )
    zabbix_send = models.BooleanField(
        default=False,
        verbose_name='Отправлять статистику Zabbix',
    )
    log = models.CharField(
        max_length=2,
        choices=LOG_CHOICES,
        default=SYSTEM,
        verbose_name='Лог',
    )
    log_file = models.CharField(
        max_length=4096,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^/[^\0]*[^\0/]+$",
                message="Путь к файлу должен соответствовать POSIX",
            ),
        ],
        verbose_name='Файл лога',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Описание',
    )

    class Meta:
        verbose_name = 'Конфигурация'
        verbose_name_plural = 'Конфигурации'
        ordering = ['-enabled', 'name', ]

    def __str__(self):
        return "{name} ({active}): {description}".format(
            name=self.name,
            active="Активна" if self.enabled else "Выключена",
            description=self.description,
        )

    def get_absolute_url(self):
        return reverse(
            'task:config:detail',
            kwargs={'slug': self.slug},
        )

    def get_update_url(self):
        return reverse(
            'task:config:update',
            kwargs={'slug': self.slug},
        )

    def get_delete_url(self):
        return reverse(
            'task:config:delete',
            kwargs={'slug': self.slug},
        )

    def clean(self):
        # Одновременно может быть включена
        # только одна конфигурация
        if self.enabled:
            enabled = Config.objects.filter(
                enabled=True,
            ).exclude(id=self.id)
            if enabled:
                raise ValidationError(
                    {
                        'enabled': ValidationError(
                            _('Одновременно может быть включена'
                              ' только одна конфигурация. В настоящее'
                              ' время включена конфигурация: %(name)s'),
                            code='invalid',
                            params={
                                # На случай если включена не одна конфигурация
                                'name': ', '.join(['"{}"'.format(config.name)
                                                   for config in enabled]),
                            },
                        )
                    },
                )


class ServerTask(models.Model):
    server = models.ForeignKey(
        Server,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Сервер',
    )
    requests = models.ManyToManyField(
        Request,
        related_name='tasks',
        verbose_name='Запросы',
    )
    timeout = models.PositiveSmallIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(60),
        ],
        verbose_name='Таймаут',
    )
    enabled = models.BooleanField(
        default=False,
        verbose_name='Активно',
    )
    executed = models.DateTimeField(
        null=True,
        verbose_name='Последний запуск',
    )
    status = models.BooleanField(
        null=True,
        verbose_name='Результат',
    )

    class Meta:
        verbose_name = 'Опрос сервера'
        verbose_name_plural = 'Опросы серверов'
        ordering = ['-enabled', 'server', ]

    def __str__(self):
        return "{pk}: {server} ({requests}) - {enabled}".format(
            pk=self.pk,
            server=self.server,
            requests=', '.join(
                [request.name for request in self.requests.all()],
            ),
            enabled='Активен' if self.enabled else 'Выключен',
        )

    def get_absolute_url(self):
        return reverse(
            'task:server:detail',
            kwargs={'pk': self.pk},
        )

    def get_update_url(self):
        return reverse(
            'task:server:update',
            kwargs={'pk': self.pk},
        )

    def get_delete_url(self):
        return reverse(
            'task:server:delete',
            kwargs={'pk': self.pk},
        )
