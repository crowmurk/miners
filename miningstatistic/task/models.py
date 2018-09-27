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

from core.validators import validate_slug

from miner.models import Server, Request

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
    )
    refresh = models.PositiveSmallIntegerField(
        default=30,
        validators=[
            MinValueValidator(10),
        ],
        help_text='Интервал опроса серверов (сек.).',
    )
    zabbix_server = models.GenericIPAddressField(
        blank=True,
        null=True,
        validators=[
            validate_ipv46_address,
        ],
    )
    zabbix_port = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(65535),
        ],
    )
    zabbix_send = models.BooleanField(
        default=False,
        help_text='Отправлять статистику Zabbix серверу.',
    )
    log = models.CharField(
        max_length=2,
        choices=LOG_CHOICES,
        default=SYSTEM,
    )
    log_file = models.CharField(
        max_length=4096,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^/[^\0]*[^\0/]+$",
                message="Путь к файлу должен соответствовать POSIX",
            ),
        ]
    )
    description = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:
        verbose_name = 'Конфигурация'
        ordering = ['-enabled', 'name', ]

    def __str__(self):
        return "{name}-{active}: {description}".format(
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


class Server(models.Model):
    server = models.ForeignKey(
        Server,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    requests = models.ManyToManyField(
        Request,
        related_name='tasks',
    )
    enabled = models.BooleanField(
        default=False,
    )
    last_executed = models.DateTimeField(
        null=True,
    )
    status = models.BooleanField(
        null=True,
        help_text='Результат последнего запуска',
    )

    class Meta:
        verbose_name = 'Опрос сервера'
        ordering = ['-enabled', 'server', ]

    def __str__(self):
        return "{pk}: {server}".format(
            pk=self.pk,
            server=self.server,
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
