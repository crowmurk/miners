import django_tables2 as tables


class ServerStatisticTable(tables.Table):
    server = tables.Column(
        linkify=(('miner:server:detail', {'slug': tables.A('server')})),
    )

    def __init__(self, *args, **kwargs):
        self.verbose_name_prefix = kwargs.pop('verbose_name_prefix', None)
        self.miner = kwargs.pop('miner', None)
        super().__init__(*args, **kwargs)

    def render_server(self, value):
        return value.upper()


class ServerStatisticErrorTable(ServerStatisticTable, tables.Table):
    error_type = tables.Column(
        verbose_name='Тип ошибки',
    )
    error_data = tables.Column(
        verbose_name='Данные',
    )
    error_message = tables.Column(
        verbose_name='Сообщение',
    )
