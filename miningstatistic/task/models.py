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

from core.validators import validate_slug, validate_json

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
    zabbix_timeout = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(60),
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
        related_name='tasks'
    )
    requests = models.ManyToManyField(
        Request,
        related_name='tasks',
    )
    timeout = models.PositiveSmallIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(60),
        ],
    )
    enabled = models.BooleanField(
        default=False,
    )
    executed = models.DateTimeField(
        null=True,
        help_text='Время последнего запуска',
    )
    status = models.BooleanField(
        null=True,
        help_text='Результат последнего запуска',
    )

    class Meta:
        verbose_name = 'Опрос сервера'
        ordering = ['-enabled', 'server', ]

    def __str__(self):
        return "{pk}: {server} ({requests}) - {enabled}".format(
            pk=self.pk,
            server=self.server,
            requests=', '.join(
                [request.name for request in self.requests.all()],
            ),
            enabled='Активно' if self.enabled else 'Выключено',
        )

    def get_absolute_url(self):
        return reverse(
            'task:servertask:detail',
            kwargs={'pk': self.pk},
        )

    def get_update_url(self):
        return reverse(
            'task:servertask:update',
            kwargs={'pk': self.pk},
        )

    def get_delete_url(self):
        return reverse(
            'task:servertask:delete',
            kwargs={'pk': self.pk},
        )


class ServerStatistic(models.Model):
    task = models.ForeignKey(
        ServerTask,
        on_delete=models.CASCADE,
        related_name='statistic',
    )
    request_id = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ],
        help_text='Идентификатор опроса',
    )
    result = models.TextField(
        validators=[
            validate_json,
        ],
        help_text='Результат выполнения задания',
    )
    executed = models.DateTimeField(
        help_text='Время выполнения задания',
    )
    status = models.BooleanField(
        help_text='Статус выполнения задания',
    )

    class Meta:
        verbose_name = 'Статистика работы серверов'
        ordering = ['-request_id', 'task', '-status']

    def __str__(self):
        return "{task} - {executed} - {status}".format(
            task=self.task,
            executed=self.executed,
            status='Успех' if self.status else 'Ошибка',
        )

    def get_absolute_url(self):
        return reverse(
            'task:servertask:statistic:detail',
            kwargs={'pk': self.pk},
        )

    def get_update_url(self):
        return reverse(
            'task:servertask:statistic:update',
            kwargs={'pk': self.pk},
        )

    def get_delete_url(self):
        return reverse(
            'task:servertask:statistic:delete',
            kwargs={'pk': self.pk},
        )
