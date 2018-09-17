from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    validate_ipv46_address
)

from core.utils import get_unique_slug
from core.validators import validate_template

# Create your models here.

class Miner(models.Model):
    name = models.CharField(max_length=31)
    version = models.CharField(max_length=31)
    slug = models.SlugField(
        max_length=63,
        unique=True,
        editable=False,
        help_text='A label for URL config.',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:
        verbose_name = 'Supported miners'
        ordering = ['name', 'version']
        unique_together = (('name', 'version'),)

    def __str__(self):
        return "{name} {version}".format(
            name=self.name,
            version=self.veersion,
        )

    def save(self, *args, **kwargs):
        self.slug = get_unique_slug(
            self, ('name', 'version'), 'slug',
        )
        super().save(*args, **kwargs)

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
    name = models.CharField(max_length=31)
    slug = models.SlugField(
        max_length=31,
        editable=False,
        help_text='A label for URL config.',
    )
    request = models.TextField(
        max_length=254,
        validators=[validate_template],
    )
    response = models.TextField(
        blank=True,
        help_text='Response template',
        validators=[validate_template],
    )
    description = models.CharField(
        max_length=255,
        blank=True,
    )
    miner = models.ForeignKey(
        Miner,
        on_delete=models.CASCADE,
        related_name='requests',
    )

    class Meta:
        verbose_name = 'Supported requests'
        ordering = ['miner', 'name']
        unique_together = (('slug', 'miner'),)

    def __str__(self):
        return "{miner} {version} - {name}".format(
            miner=self.miner.name,
            version=self.miner.version,
            name=self.name,
        )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return self.miner.get_absolute_url()

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
    )
    slug = models.SlugField(
        max_length=31,
        unique=True,
        editable=False,
        help_text='A label for URL config.',
    )
    host = models.GenericIPAddressField(
        validators=[
            validate_ipv46_address,
        ]
    )
    port = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(65535),
        ]
    )
    miner = models.ForeignKey(
        Miner,
        on_delete=models.CASCADE,
        related_name='servers'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:
        verbose_name = 'Mining servers'
        ordering = ['name']

    def __str__(self):
        return "{name} - {host}:{port} ({miner} {version})".format(
            name=self.name,
            host=self.host,
            port=self.port,
            miner=self.miner.name,
            version=self.miner.version,
        )

    def save(self, *args, **kwargs):
        self.slug = get_unique_slug(
            self, 'name', 'slug',
        )
        super().save(*args, **kwargs)

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
