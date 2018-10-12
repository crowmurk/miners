from django.apps import AppConfig


class StatisticConfig(AppConfig):
    name = 'statistic'

    def ready(self):
        import core.signals
