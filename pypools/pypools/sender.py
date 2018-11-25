#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Модуль содержит реализацию класса Sender
"""

from copy import deepcopy
from validictory import validate

from .nanopool import NanoPool
from .flypool import FlyPool

class Sender():
    """Опрашивает пулы из переданного списка
    """
    def __init__(self, pools):
        """ Аргументы:
        pools: список для опроса пулов в формате dict:
        {PoolName: {'Pool': str, 'Coin': str, 'Host': str,
                    'Port': int, 'Timeout': int, 'Account': str,
                    'Request': dict, 'Workers': list, }, }
        где:
            Pool - тип пула
            Coin - тип монеты
            Host - адрес пула
            Port - порт пула
            Timeout - таймаут ожидания ответа от пула
            Account - идинтификатор аккаутнта на пуле
            Request - запрос к пулу в формате dict:
                {'Name': str, 'Args': dict}
                где:
                    Name - запрос
                    Args - аргументы запроса в виде словаря
            Workers - ожидаемые майнеры на пуле
        """
        self.__supportedPools = {
            'NanoPool': NanoPool,
            'FlyPool': FlyPool,
        }
        self.__results = {}
        self.pools = pools

    @property
    def supportedPools(self):
        """Поддерживаемые пулы
        """
        return self.__supportedPools.keys()

    @property
    def pools(self):
        """Список параметров опроса пулов в формате dict:
           {PoolName: {'Pool': str, 'Coin': str, 'Host': str,
                       'Port': int, 'Timeout': int, 'Account': str,
                       'Request': str, 'Workers': list, }, }
        """
        try:
            return deepcopy(self.__pools)
        except AttributeError:
            return None

    @pools.setter
    def pools(self, value):
        """Параметры опроса пулов, должны быть в формате dict следующего вида:
           {PoolName: {'Pool': str, 'Coin': str, 'Host': str,
                       'Port': int, 'Timeout': int, 'Account': str,
                       'Request': str, 'Workers': list, }, } """

        # Шаблон для проверки параметров опроса пула
        template = {
            "type": "object",
            "properties": {
                "Pool": {"type": "string"},
                "Coin": {"type": "string"},
                "Host": {"type": "string"},
                "Port": {"type": "integer"},
                "Timeout": {"type": "integer"},
                "Account": {"type": "string"},
                "Workers": {"type": "array"},
                "Request": {
                    "type": "object", "properties": {
                        "Name": {"type": "string"},
                        "Args": {
                            "type": "object", "properties": {
                                "worker": {"type": ["string", "null"]},
                                "hours": {"type": ["integer", "null"]},
                            },
                        },
                    },
                },
            },
        }

        # Если передан не словарь
        if not isinstance(value, dict):
            raise ValueError(
                "pools list must be dictionary",
            )

        # Проверяем настройки для каждого пула на соответвие шаблону
        for item in value:
            try:
                validate(
                    value[item],
                    template,
                    disallow_unknown_properties=True,
                )
                if value[item]['Pool'] not in self.supportedPools:
                    raise ValueError(
                        "Pool = '{pool}' not supported".format(
                            pool=value[item]['Pool'],
                        ),
                    )
            except ValueError as e:
                raise ValueError(
                    "pool = '{pool}' error in pool"
                    " settings ({error})".format(
                        pool=item,
                        error=e,
                    ),
                ) from None

        self.__pools = deepcopy(value)

    @property
    def results(self):
        """Результаты опроса пулов в формате dict
        """
        try:
            return deepcopy(self.__results)
        except AttributeError:
            return None

    @property
    def union(self):
        """Результаты опроса пулов, в формате dict
        с параметрами запросов и полученными ответами
        """
        union = deepcopy(self.results)
        # Порядок ключей в возвращаемом словаре
        keys = [
            'Pool', 'Coin', 'Host', 'Port', 'Timeout',
            'Account', 'Request', 'Workers', 'Result', 'Error',
        ]
        # Объединяем словари с настройками запросов к пулам и ответами
        for name in union:
            union[name].update(self.pools[name])
            union[name] = {key: union[name][key] for key in keys}
        return union

    def sendRequests(self):
        """Опрашивает пулы
        """
        for name, settings in self.pools.items():
            # Инициализируем экземпляр
            pool = self.__supportedPools[settings['Pool']](
                settings['Account'],
                settings['Coin'],
                pool=settings['Host'],
                port=settings['Port'],
                timeout=settings['Timeout'],
            )
            # Отправляем запрос
            getattr(pool, settings['Request']['Name'])(
                **settings['Request']['Args'],
            )
            # Сохраняем результат
            self.__results[name] = {
                'Result': pool.response,
                'Error': pool.error,
            }
