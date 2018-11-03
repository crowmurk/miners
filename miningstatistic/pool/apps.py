from django.apps import AppConfig


class PoolConfig(AppConfig):
    name = 'pool'

    def ready(self):
        import core.signals
