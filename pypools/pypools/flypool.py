#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Модуль содержит реализацию класса FlyPool
"""

from .pool import Pool

class FlyPool(Pool):
    """Отправляет запросы к пулу FlyPool
    """
    def __init__(
            self,
            account,
            coin=None,
            *,
            pool='api-zcash.flypool.org',
            port=443,
            timeout=5,
    ):
        """Аргументы:
        account: id аккаунта на пуле
        pool: адрес пула
        port: порт пула
        timeout: время ожидания ответа пула
        """

        # Поддерживаемы запросы
        self.__queries = {
            'getMinerDashboard': 'dashboard',
            'getMinerHistory': 'history',
            'getMinerPayouts': 'payouts',
            'getMinerSettings': 'settings',
            'getMinerStatistics': 'currentStats',
            'getWorkerAllStatistics': 'workers',
            'getWorkerWorkerMonitoring': 'workers/monitor',
            'getWorkerIndividualHistoricalStatistics': 'worker/{worker}/history',
            'getWorkerIndividualStatistics': 'worker/{worker}/currentStats',
        }

        super().__init__(pool, port, timeout)
        self.account = account

    @property
    def queries(self):
        """Поддерживаемые запросы
        """
        return sorted(tuple(self.__queries))

    @property
    def account(self):
        """Аккаунт
        """
        try:
            return self.__account
        except AttributeError:
            return None

    @account.setter
    def account(self, value):
        """Аккаунт должен быть строкой ненулевой длины
        """
        if value and isinstance(value, str):
            self.__account = value
        else:
            raise ValueError(
                "invalid account '{account}'".format(
                    account=value,
                ),
            )

    def __getattr__(self, query):
        """Запросы к пулу согласно api
        """
        # Если запрос поддерживается
        if query in self.__queries:
            def wrapper(*, worker=None, hours=None):
                # Формируем url
                url = '/miner/{account}/{query}'.format(
                    account=self.__account,
                    query=self.__queries[query],
                )
                if worker:
                    url = url.format(worker=worker)
                elif '{worker}' in url:
                    raise TypeError(
                        "{function}() missing 1 required"
                        " positional argument".format(
                            function=query,
                        ),
                    )
                # Отправляем запрос
                self.sendRequest(url)
                return self.response
            return wrapper
        else:
            # Запрос не поддерживается
            raise AttributeError(
                "atribute '{attribute}' does not"
                " exist in {obj}".format(
                    attribute=query,
                    obj=self.__class__,
                ),
            )
