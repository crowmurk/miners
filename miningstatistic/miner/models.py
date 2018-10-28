from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
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
        verbose_name=_('Miner'),
    )
    version = models.CharField(
        max_length=31,
        verbose_name=_('Version'),
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
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Description'),
    )

    class Meta:
        verbose_name = _('Miner')
        verbose_name_plural = _('Miners')
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
        verbose_name=_('Name'),
    )
    slug = models.SlugField(
        max_length=31,
        editable=False,
        validators=[
            validate_slug,
        ],
        help_text=_('A label for URL config.'),
    )
    request = models.TextField(
        max_length=255,
        validators=[
            validate_json,
        ],
        verbose_name=_('Request'),
    )
    response = models.TextField(
        blank=True,
        validators=[
            validate_json,
        ],
        verbose_name=_('Response'),
        help_text=_('Response template'),
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Description'),
    )
    miner = models.ForeignKey(
        Miner,
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name=_('Miner'),
    )

    class Meta:
        verbose_name = _('Request')
        verbose_name_plural = _('Requests')
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
        verbose_name=_('Name'),
    )
    slug = models.SlugField(
        max_length=31,
        unique=True,
        editable=False,
        validators=[
            validate_slug,
        ],
        help_text=_('A label for URL config.'),
    )
    host = models.GenericIPAddressField(
        validators=[
            validate_ipv46_address,
        ],
        verbose_name=_('IP address'),
    )
    miner = models.ForeignKey(
        Miner,
        on_delete=models.CASCADE,
        related_name='servers',
        verbose_name=_('Miner'),
    )
    port = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(65535),
        ],
        verbose_name=_('Port'),
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Description'),
    )

    class Meta:
        verbose_name = _('Server')
        verbose_name_plural = _('Servers')
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
