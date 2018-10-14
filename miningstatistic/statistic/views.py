import json

from django.utils import timezone
from django.views.generic.base import TemplateView

from django_tables2 import MultiTableMixin, Column

from task.models import Config
from miner.models import Miner

from .models import ServerStatistic
from .tables import (
    ServerStatisticErrorTable,
    ServerStatisticTable
)

# Create your views here.

class ServerStatisticList(MultiTableMixin, TemplateView):
    template_name = 'statistic/serverstatistic_list.html'

    def get_tables(self):
        def get_data_list(data):
            """Возвращает список с данными
            для наполнения таблицы
            """
            data_list = []
            for server, result in data.values_list(
                    'task__server__slug',
                    'result',
            ):
                result = json.loads(result)
                result['server'] = server
                data_list.append(result)
            return data_list

        # Список таблиц для представления
        tables = []

        # Результаты последнего опроса
        last_data = ServerStatistic.objects.results_last()

        for miner in Miner.objects.all():
            # Сооздаем таблицу с ошибками
            data = last_data.filter(
                status=False,
                task__server__miner=miner,
            )
            if data:
                table = ServerStatisticErrorTable(
                    get_data_list(data),
                    verbose_name_prefix='Ошибки',
                    miner=miner,
                )
                tables.append(table)

            # Создаем таблицу со статистикой
            data = last_data.filter(
                status=True,
                task__server__miner=miner,
            )
            if data:
                data = get_data_list(data)
                table = ServerStatisticTable(
                    data,
                    extra_columns=[(name, Column())
                                   for name in data[0].keys()
                                   if name != 'server'],
                    verbose_name_prefix='Статистика',
                    miner=miner,
                )
                tables.append(table)

        return tables

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['update_interval'] = Config.objects.get(enabled=True).refresh
        return context
