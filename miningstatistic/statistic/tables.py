import django_tables2 as tables

from .models import ServerStatistic

class ServerStatisticTable(tables.Table):
    class Meta:
        model = ServerStatistic
