import django_tables2 as tables


class ServerStatisticTableMixin(tables.Table):
    server = tables.Column(
        linkify=(('miner:server:detail', {'slug': tables.A('server')})),
        verbose_name='Сервер',
    )

    def render_server(self, value):
        return value.upper()


class ServerStatisticErrorTable(ServerStatisticTableMixin, tables.Table):
    verbose_name = 'Ошибки'

    error_type = tables.Column(
        verbose_name='Тип ошибки',
    )
    error_data = tables.Column(
        verbose_name='Данные',
    )
    error_message = tables.Column(
        verbose_name='Сообщение',
    )


class ServerStatisticEtheriumTable(ServerStatisticTableMixin, tables.Table):
    verbose_name = 'Статистика Etherium'

    uptime = tables.Column()
    eth = tables.Column(
        verbose_name='ETH',
    )
    eth_per_gpu = tables.Column(
        verbose_name='ETH/GPU',
    )
    dcr = tables.Column(
        verbose_name='DCR',
    )
    dcr_per_gpu = tables.Column(
        verbose_name='DCR/GPU',
    )
    gpu = tables.Column(
        verbose_name='Параметры GPU',
    )
    pools = tables.Column(
        verbose_name='Пулы',
    )


class ServerStatisticCGMinerTable(ServerStatisticTableMixin, tables.Table):
    verbose_name = 'Статистика CGMiner'

    elapsed = tables.Column(
        verbose_name='Uptime',
    )
    accepted = tables.Column()
    rejected = tables.Column()
    ghs_av = tables.Column(
        verbose_name='GHS среднее',
    )
    hardware_errors = tables.Column()
    discarded = tables.Column()
    dev_pool_rejected = tables.Column(
        verbose_name='Dev/Pool Rejected (%)',
    )
    last_getwork = tables.Column()
    fans = tables.Column()
    temps_1 = tables.Column()
    temps_2 = tables.Column()
    description = tables.Column(
        verbose_name='Описание',
    )

    class Meta:
        exclude = ('description', )


class ServerStatisticZCashTable(ServerStatisticTableMixin, tables.Table):
    verbose_name = 'Статистика ZCash'

    gpu_status = tables.Column(
        verbose_name='GPU Статус',
    )
    temperature = tables.Column(
        verbose_name='Температура',
    )
    gpu_power_usage = tables.Column(
        verbose_name='GPU Потребление',
    )
    speed_sps = tables.Column(
        verbose_name='Решено/сек.',
    )
    accepted_shares = tables.Column(
        verbose_name='Accepted Shares',
    )
    rejected_shares = tables.Column(
        verbose_name='Rejected Shares',
    )
