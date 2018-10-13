from django.views.generic.base import TemplateView

from django_tables2 import MultiTableMixin

from .models import ServerStatistic
from .tables import (
    ServerStatisticErrorTable,
    ServerStatisticEtheriumTable,
    ServerStatisticZCashTable,
    ServerStatisticCGMinerTable,
)

# Create your views here.


class ServerStatisticList(MultiTableMixin, TemplateView):
    template_name = 'statistic/serverstatistic_list.html'
    tables = [
        ServerStatisticErrorTable,
        ServerStatisticEtheriumTable,
        ServerStatisticZCashTable,
        ServerStatisticCGMinerTable,
    ]

    def get_tables_data(self):
        tables_data = [
            ServerStatistic.objects.results_last().filter(
                status=False,
            ).table_data(),
        ]
        for miner_slug in (
                'claymores-dual-ethereum-amd-gpu-98',
                'ewbfs-cuda-zcash-034b',
                'antminer-s9-cgminer-490',
        ):
            tables_data.append(
                ServerStatistic.objects.results_last().filter(
                    status=True,
                    task__server__miner__slug=miner_slug
                ).table_data())
        return tables_data
