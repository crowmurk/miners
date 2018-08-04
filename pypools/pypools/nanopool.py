#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Модуль содержит реализацию класса NanoPool"""

from .pool import Pool

class NanoPool(Pool):
    """Отправляет запросы к пулу NanoPool"""
    def __init__(self, account, coin, *, pool='api.nanopool.org', port=443, timeout=5):
        """
            Аргументы:
                account: id аккаунта на пуле
                coin: тип монеты
                    Поддерживаемые монеты (см. свойство coins)
                pool: адрес пула
                port: порт пула
                timeout: время ожидания ответа пула

            Поддерживаемые запросы  см. свойство queries"""

        # Поддерживаемы монеты
        self.__coins = {'Etherium': 'eth', 'Monero': 'xmr'}

        # Поддерживаемы запросы
        self.__queries = {'getMinerAccountBalance': 'balance', 'getWorkerCurrentHashrate': 'balance',
                          'getMinerCheckMinerAccount': 'accountexist', 'getMinerCurrentHashrate': 'hashrate',
                          'getMinerGeneralInfo': 'user', 'getMinerHashrateAndBalance': 'balance_hashrate',
                          'getMinerListOfWorker': 'workers', 'getMinerPayments': 'payments',
                          'getMinerPaymentsDay': 'paymentsday', 'getMinerWorkersLastReportedHashrate': 'reportedhashrates',
                          'getUserSettings': 'usersettings', 'getMinerAverageHashrates': 'avghashrate',
                          'getMinerChartData': 'hashratechart', 'getMinerHashrateHistory': 'history',
                          'getMinerLastReportedHashrateForAccount': 'reportedhashrate',
                          'getMinerShareRateHistory': 'shareratehistory',
                          'getMinerWorkersAverageHashrates': 'avghashrateworkers'}

        # Поддерживаемы запросы с указанием промежутка времени
        self.__queriesHours = {'getMinerAverageHashrate': 'avghashratelimited',
                               'getMinerWorkersAverageHashrate': 'avghashrateworkers',
                               'getWorkerAverageHashrate': 'avghashratelimited'}

        # Поддерживаемы запросы с указанием worker'a
        self.__queriesWorker = {'getWorkerAverageHashrates': 'avghashrate', 'getWorkerChartData': 'hashratechart',
                                'getWorkerHashrateHistory': 'history', 'getWorkerLastReportedHashrateForWorker': 'reportedhashrate',
                                'getWorkerShareRateHistory': 'shareratehistory', 'getWorkerAverageHashrate': 'avghashratelimited'}

        # Поддерживаемые интервалы времени
        self.__hoursIntervals = (1, 3, 6, 12, 24)

        super().__init__(pool, port, timeout)
        self.coin = coin
        self.account = account

    @property
    def coins(self):
        """Поддерживаемые монеты"""
        return tuple(self.__coins)

    @property
    def queries(self):
        """Поддерживаемые запросы"""
        return set(tuple(self.__queries) + tuple(self.__queriesHours) + tuple(self.__queriesWorker))

    @property
    def coin(self):
        """"Тип монеты"""
        try:
            return self.__coin
        except AttributeError:
            return None

    @coin.setter
    def coin(self, value):
        """Тип монеты должен поддерживаться пулом"""
        if value in self.__coins:
            self.__coin = self.__coins[value]
        else:
            raise ValueError("coin '{coin}' not supported by nanopool.org".format(coin=value))

    @property
    def account(self):
        """Аккаунт"""
        try:
            return self.__account
        except AttributeError:
            return None

    @account.setter
    def account(self, value):
        """Аккаунт должен быть строкой ненулевой длины"""
        if value and isinstance(value, str):
            self.__account = value
        else:
            raise ValueError("invalid account '{account}'".format(account=value))

    def __getattr__(self, query):
        """Запросы к пулу согласно api"""
        # Если запрос поддерживается
        if query in self.queries:
            def wrapper(*, hours=None, worker=None):
                # Формируем url
                for item in (self.__queries, self.__queriesHours, self.__queriesWorker):
                    if query in item:
                        urlQuery = item[query]
                url = '/v1/{coin}/{query}/{account}'.format(coin=self.__coin, account=self.__account, query=urlQuery)
                # Если задан параметр
                if worker:
                    # И он поддерживается
                    if query in self.__queriesWorker:
                        url += '/{worker}'.format(worker=worker)
                    else:
                        raise TypeError("{function}() got an unexpected keyword argument 'worker'".format(function=query))

                # Если задан параметр
                if hours:
                    # Задано допустимое значение
                    if isinstance(hours, int) and hours in self.__hoursIntervals:
                        # И он поддерживается
                        if query in self.__queriesHours:
                            url += '/{hours}'.format(hours=hours)
                        else:
                            raise TypeError("{function}() got an unexpected keyword argument 'hours'".format(function=query))
                    else:
                        raise ValueError("request period '{hours}' must be in {intervals}".format(hours=hours, intervals=self.__hoursIntervals))
                # Если параметр не задан, но требуется
                elif query in self.__queriesHours:
                    raise TypeError("{function}() missing 1 required keyword argument 'hours'".format(function=query))

                # Отправляем запрос
                self.sendRequest(url)
                return self.response
            return wrapper
        else:
            # Запрос не поддерживается
            raise AttributeError("atribute '{attribute}' does not exist in {obj}".format(attribute=query, obj=self.__class__))
