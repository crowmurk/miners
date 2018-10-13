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
    model = ServerStatistic
    tables = [
        ServerStatisticErrorTable,
        ServerStatisticEtheriumTable,
        ServerStatisticZCashTable,
        ServerStatisticCGMinerTable,
    ]
    tables_data = [
        model.objects.results_last().filter(
            status=False,
        ).table_data(),
        model.objects.results_last().filter(
            status=True,
            task__server__miner__slug='claymores-dual-ethereum-amd-gpu-98',
        ).table_data(),
        model.objects.results_last().filter(
            status=True,
            task__server__miner__slug='ewbfs-cuda-zcash-034b',
        ).table_data(),
        model.objects.results_last().filter(
            status=True,
            task__server__miner__slug='antminer-s9-cgminer-490',
        ).table_data(),
    ]
