from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    validate_ipv46_address,
    RegexValidator,
)
from django.core.exceptions import ValidationError

from core.validators import validate_slug

from miner.models import Server, Request

# Create your models here.

class Config(models.Model):
    NOLOG = 'NO'
    SYSTEM = 'SY'
    STDOUT = 'ST'
    FILE = 'FI'

    LOG_CHOICES = (
        (NOLOG, _('Disabled')),
        (SYSTEM, _('Systemd journal')),
        (STDOUT, _('STDOUT')),
        (FILE, _('File')),
    )

    name = models.CharField(
        max_length=31,
        unique=True,
        verbose_name=_('Name'),
    )
    slug = models.SlugField(
        max_length=63,
        unique=True,
        editable=False,
        validators=[
            validate_slug,
        ],
        help_text=_('A label for URL config.'),
    )
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Status'),
    )
    refresh = models.PositiveSmallIntegerField(
        default=30,
        validators=[
            MinValueValidator(10),
        ],
        verbose_name=_('Request interval'),
        help_text=_('Request interval (sec.).'),
    )
    zabbix_server = models.GenericIPAddressField(
        blank=True,
        null=True,
        validators=[
            validate_ipv46_address,
        ],
        verbose_name=_('Zabbix host'),
    )
    zabbix_port = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(65535),
        ],
        verbose_name=_('Zabbix port'),
    )
    zabbix_timeout = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(60),
        ],
        verbose_name=_('Zabbix timeout'),
    )
    zabbix_send = models.BooleanField(
        default=False,
        verbose_name=_('Send statistic to Zabbix'),
    )
    log = models.CharField(
        max_length=2,
        choices=LOG_CHOICES,
        default=SYSTEM,
        verbose_name=_('Log'),
    )
    log_file = models.CharField(
        max_length=4096,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^/[^\0]*[^\0/]+$',
                message=_('Path to the file must follow POSIX'),
            ),
        ],
        verbose_name=_('Log file'),
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Description'),
    )

    class Meta:
        verbose_name = _('Configuration')
        verbose_name_plural = _('Configurations')
        ordering = ['-enabled', 'name', ]

    def __str__(self):
        return '{name} ({enabled}): {description}'.format(
            name=self.name,
            enabled=_('Enabled') if self.enabled else _('Disabled'),
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
                            _('Only one config can be enabled at a time.'
                              ' "%(name)s" config is now enabled.'),
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
        verbose_name=_('Server'),
    )
    requests = models.ManyToManyField(
        Request,
        related_name='tasks',
        verbose_name=_('Requests'),
    )
    timeout = models.PositiveSmallIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(60),
        ],
        verbose_name=_('Timeout'),
    )
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Status'),
    )
    executed = models.DateTimeField(
        null=True,
        verbose_name=_('Last executed'),
    )
    status = models.BooleanField(
        null=True,
        verbose_name=_('Last status'),
    )

    class Meta:
        verbose_name = _('Server request')
        verbose_name_plural = _('Servers requests')
        ordering = ['-enabled', 'server', ]

    def __str__(self):
        return '{pk}: {server} ({requests}) - {enabled}'.format(
            pk=self.pk,
            server=self.server,
            requests=', '.join(
                [request.name for request in self.requests.all()],
            ),
            enabled=_('Enabled') if self.enabled else _('Disabled'),
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
