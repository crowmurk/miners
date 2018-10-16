from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator

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
        verbose_name='Задание',
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
        verbose_name='Результат опроса',
    )
    executed = models.DateTimeField(
        verbose_name='Время выполнения',
    )
    status = models.BooleanField(
        verbose_name='Статус завершения',
    )

    objects = ServerStatisticQueryset.as_manager()

    class Meta:
        verbose_name = 'Статистика сервера'
        verbose_name_plural = 'Статистика серверов'
        ordering = ['-request_id', 'task', '-status']

    def __str__(self):
        return "{task} - {executed} - {status}".format(
            task=self.task,
            executed=self.executed,
            status='Успех' if self.status else 'Ошибка',
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
