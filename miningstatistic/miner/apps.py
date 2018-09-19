from django.apps import AppConfig


class MinerConfig(AppConfig):
    name = 'miner'

    def ready(self):
        import core.signals
