import django_tables2 as tables


class ServerStatisticTable(tables.Table):
    server = tables.Column(
        linkify=(('miner:server:detail', {'slug': tables.A('server')})),
        verbose_name='Сервер',
    )

    def __init__(self, *args, **kwargs):
        self.verbose_name_prefix = kwargs.pop('verbose_name_prefix', None)
        self.miner = kwargs.pop('miner', None)
        self.rename_columns(kwargs.get('extra_columns', None))
        super().__init__(*args, **kwargs)

    def rename_columns(self, columns):
        """Переименовывает заголовки таблиц
        для известных майнеров"""
        if not columns:
            return None

        mappings = {
            'antminer-s9-cgminer-490': {
                'elapsed': 'Uptime',
                'accepted': 'Accepted',
                'rejected': 'Rejected',
                'ghs_av': 'GHS Avg.',
                'hardware_errors': 'HW Errors',
                'discarded': 'Discarded',
                'dev_pool_rejected': 'Dev/Pool Rej. (%)',
                'last_getwork': 'Last getwork',
                'fans': 'Fans (rpm)',
                'temps_1': 'Temps1 (°C)',
                'temps_2': 'Temps2 (°C)',
                'description': 'Описание',
            },
            'claymores-dual-ethereum-amd-gpu-98': {
                'uptime': 'Uptime',
                'eth': 'ETH',
                'eth_per_gpu': 'ETH / GPU',
                'dcr': 'DCR',
                'dcr_per_gpu': 'DCR / GPU',
                'gpu': 'GPU',
                'pools': 'Пулы',
            },
            'ewbfs-cuda-zcash-034b': {
                'gpu_status': 'GPU',
                'temperature': 'Temps (°C)',
                'gpu_power_usage': 'GPU Power Usage',
                'speed_sps': 'Speed (Sol./sec.)',
                'accepted_shares': 'Accepted',
                'rejected_shares': 'Rejected',
            },
        }
        mappings[
            'claymores-cryptonote-gpu-97'
        ] = mappings['claymores-dual-ethereum-amd-gpu-98']

        mapping = mappings.get(self.miner.slug, None)
        if mapping:
            for name, column in columns:
                if name in mapping:
                    column.verbose_name = mapping[name]

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
