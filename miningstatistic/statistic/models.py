from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from task.models import ServerTask
from core.validators import validate_json

# Create your models here.

class ServerStatisticQueryset(models.QuerySet):
    def results_last(self):
        if ServerStatistic.objects.count():
            request_id_max = ServerStatistic.objects.aggregate(
                models.Max('request_id'),
            )['request_id__max']
        else:
            request_id_max = 0
        return self.filter(request_id=request_id_max)


class ServerStatistic(models.Model):
    task = models.ForeignKey(
        ServerTask,
        on_delete=models.CASCADE,
        related_name='statistic',
        verbose_name=_('Task'),
    )
    request_id = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ],
        help_text=_('Request ID'),
    )
    result = models.TextField(
        validators=[
            validate_json,
        ],
        verbose_name=_('Request result'),
    )
    executed = models.DateTimeField(
        verbose_name=_('Executed at'),
    )
    status = models.BooleanField(
        verbose_name=_('Request status'),
    )

    objects = ServerStatisticQueryset.as_manager()

    class Meta:
        verbose_name = _('Server statistic')
        verbose_name_plural = _('Servers statistics')
        ordering = ['-request_id', 'task', '-status']

    def __str__(self):
        return "{task} - {executed} - {status}".format(
            task=self.task,
            executed=self.executed,
            status=_('Success') if self.status else _('Failure'),
        )

    def get_absolute_url(self):
        return reverse(
            'statistic:server:detail',
            kwargs={'pk': self.pk},
        )

    def get_update_url(self):
        return reverse(
            'statistic:server:update',
            kwargs={'pk': self.pk},
        )

    def get_delete_url(self):
        return reverse(
            'statistic:server:delete',
            kwargs={'pk': self.pk},
        )
