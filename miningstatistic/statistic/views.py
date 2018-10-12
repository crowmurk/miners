from django_tables2 import SingleTableView

from .models import ServerStatistic
from .tables import ServerStatisticTable

# Create your views here.


class ServerStatisticList(SingleTableView):
    table_class = ServerStatisticTable
    model = ServerStatistic
    queryset = ServerStatistic.objects.results_last()
