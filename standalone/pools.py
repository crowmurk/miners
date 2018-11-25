#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль для опроса пулов.
    Читает из конфигурационного файла параметры опроса пулов, опрашивает их,
    отпраляет полученную статистику на Zabbix сервер."""

__version__ = "1.0.1"
__author__ = "varga"

import sys
import os
import socket
import logging
from ipaddress import ip_address
from copy import deepcopy
from collections import namedtuple
from systemd import journal
from validate import Validator
from configobj import ConfigObj, ConfigObjError, flatten_errors, get_extra_values
from pyzabbix import ZabbixMetric, ZabbixSender
from pypools import Sender

class ConfigParser():
    """Загружает настройки для работы скрипта"""
    def __init__(self, config='pools.conf'):
        """
           Аргументы:
               config: путь к файлу конфигурации"""

        # Шаблон файла конфигурации
        template = """
        [Script]
            Debug = boolean(default=False)
        [Zabbix]
            Server = ip_addr(default=127.0.0.1)
            Port = integer(min=1, max=65535, default=10051)
            Send = boolean(default=True)
            Log = string(default=False)
        [__many__]
            Pool = option('FlyPool', 'NanoPool')
            Coin = option('Etherium', 'Monero', 'ZCash')
            Host = string
            Port = integer(min=1, max=65535, default=443)
            Timeout= integer(min=1, max=60, default=5)
            Account = string
            Workers = string_list
            [[Request]]
                Name = string
                [[[Args]]]
                worker = string(default=None)
                hours = integer(min=1, max=24, default=None)
        """

        # Загружаем конфигурацию
        try:
            self.__config = ConfigObj(config, configspec=template.split('\n'), file_error=True)
        except (ConfigObjError, IOError) as e:
            # Ошибка загрузки конфигурации
            raise IOError("could not read config file'{file}': {error}".format(file=config, error=e)) from None

        # Проверяем файл конфигурации
        validator = Validator()
        result = self.__config.validate(validator, preserve_errors=True)

        # Если возникли ошибки
        if result is not True:
            for (sections, key, result) in flatten_errors(self.__config, result):
                if key is not None:
                    raise ValueError("the key '{key}' in the section '{section}' of config file failed validation: {result}".format(
                        key=key, section=', '.join(sections), result=result if result else "missing key"))
                else:
                    raise ValueError("the following section in config file was missing: '{section}'".format(
                        section=', '.join(sections)))

        # Проверяем на наличие дополнительных параметров
        for section, key in get_extra_values(self.__config):
            raise ValueError("extra section or key '{key}' in section '{section}' of config file".format(
                key=key, section=', '.join(section) if section else None))

    @property
    def script(self):
        """Параметры работы скрипта, представлены как свойства объекта"""
        try:
            return namedtuple('script', [item.lower() for item in self.__config['Script'].keys()])(*self.__config['Script'].values())
        except AttributeError:
            return None

    @property
    def zabbix(self):
        """Параметры Zabbix сервера, представлены как свойства объекта"""
        try:
            return namedtuple('zabbix', [item.lower() for item in self.__config['Zabbix'].keys()])(*self.__config['Zabbix'].values())
        except AttributeError:
            return None

    @property
    def pools(self):
        """Список параметров опроса пулов в формате dict"""
        try:
            return {item: value for item, value in self.__config.items() if item not in ['Script', 'Zabbix']}
        except AttributeError:
            return None


class Zabbix():
    """Отправляет результаты опроса пулов на Zabbix серввер"""
    def __init__(self, pools, server='127.0.0.1', port=10051, log='False'):
        """
            Аргументы:
                pools: результаты опроса пулов, в формате dict:
                    {PoolID: {'Pool': str, 'Coin': str, 'Host': str, 'Port': int, 'Timeout': int,
                    'Account': str, 'Request': dict, 'Workers': list, 'Result': dict, 'Error': bool}, }
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
                        Result - ответ от пула
                        Error - статус опроса пула
                server: адрес сервера
                port: порт сервера
                log: логирование результатов работы, может принимать значения:
                    False - не вести лог
                    system - записть в системный лог systemd
                    stdout - вывод в стандартный поток
                    или принимает имя файла для записи лога"""

        self.__supportedPools = {'FlyPool': self.__flyPool,
                                 'NanoPool': self.__nanoPool}

        self.pools = deepcopy(pools)
        self.server = server
        self.port = port
        self.log = log

        self.__createMetrics()

    @property
    def server(self):
        """Адрес сервера"""
        try:
            return self.__server
        except AttributeError:
            return None

    @server.setter
    def server(self, value):
        """Адрес сервера, должен быть из диапазона частных сетей"""
        try:
            address = ip_address(value)
        except ValueError as e:
            raise ValueError("server = {message}".format(message=e)) from None

        if address.is_private:
            self.__server = value
        else:
            raise ValueError("server = '{address}' address does not appear to be in private network".format(address=address))

    @property
    def port(self):
        """Порт сервера"""
        try:
            return self.__port
        except AttributeError:
            return None

    @port.setter
    def port(self, value):
        """Порт сервера, должен находится в передлах от 1  до 65535 и быть целым числом"""
        if value in range(1, 65536):
            self.__port = value
        else:
            raise ValueError("port = '{port}' port must be in range 1..65535".format(port=value))

    @property
    def log(self):
        """log: логирование результатов работы"""
        try:
            return self.__logger
        except AttributeError:
            return None

    @log.setter
    def log(self, value):
        """log: логирование результатов работы, может принимать значения:
               False - не вести лог
               system - записть в системный лог systemd
               stdout - вывод в стандартный поток
               или принимает имя файла для записи лога"""

        journalName = os.path.basename(__file__) if __name__ == "__main__" else __name__
        timeformat = "%Y.%m.%d-%H:%M:%S"

        self.__logger = logging.getLogger(journalName)
        self.__logger.setLevel(logging.INFO)

        if value == 'False':
            # Не вести лог
            handler = logging.NullHandler()
            formatter = logging.Formatter()
        elif value == 'journal':
            # Запись лога в системный журнал
            handler = journal.JournalHandler(SYSLOG_IDENTIFIER=journalName)
            formatter = logging.Formatter('%(levelname)s: %(message)s')
        elif value == 'stdout':
            # Вывод лога в stdout
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('[%(asctime)s] %(name)s: %(levelname)s: %(message)s', timeformat)
        else:
            # Запись лога в файл
            handler = logging.FileHandler(value)
            formatter = logging.Formatter('[%(asctime)s] %(name)s: %(levelname)s: %(message)s', timeformat)

        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        self.__logger.addHandler(handler)

    @property
    def metrics(self):
        try:
            self.__metrics
        except AttributeError:
            return None

        return deepcopy(self.__metrics)

    def send(self):
        """Отправляет статистику работы майнеров на пуле на серввер"""

        for name, metrics in self.__metrics.items():
            server = ZabbixSender(self.server, self.port, chunk_size=len(metrics))
            try:
                self.log.info("metrics sended to {server}:{port} for {miner} ({result})".format(
                    server=self.server, port=self.port, miner=name, result=server.send(metrics)))
            except socket.error as e:
                self.log.error("error on sending metrics to {server}:{port} for {miner} ({message})".format(
                    server=self.server, port=self.port, miner=name, message=e))
                break

    def __createMetrics(self):
        """Формирует метрики для отправки статистики на сервер"""
        self.__metrics = {}

        for _, data in self.pools.items():
            # Если при опросе пула произошла ошибка
            if data['Error']:
                # Создаем соответвующие метрики
                for worker in data['Workers']:
                    self.__metrics[worker] = [ZabbixMetric(worker, 'pool.status', 0), ]
                # Записываем сообщение в лог
                self.log.error("error in request for pool at {host}:{port} ({message})".format(
                    host=data['Host'], port=data['Port'], message=data['Result']))
            else:
                # Добавляем метрики для всех майнеров
                self.__metrics.update(self.__supportedPools[data['Pool']](data['Workers'], data['Result']))

    @staticmethod
    def __flyPool(workers, data):
        metrics = {}
        # Если статус в ответе от пула отрицательный
        if data['status'] != 'OK':
            for worker in workers:
                metrics[worker] = [ZabbixMetric(worker, 'pool.status', 1), ]
                metrics[worker].append(ZabbixMetric(worker, 'pool.answer.status', 0))
            return metrics

        # Hashrate майнеров на пуле
        poolWorkersHashrate = {item['worker']: item['reportedHashrate'] for item in data['data']}
        # Для каждого ожидаемого на пуле майнера
        for worker in workers:
            # Статус пула
            metrics[worker] = [ZabbixMetric(worker, 'pool.status', 1), ]
            metrics[worker].append(ZabbixMetric(worker, 'pool.answer.status', 1))
            # TODO Дима, переименуй майнеры !!!
            # Если присутствует на пуле
            if worker.lower() in poolWorkersHashrate:
                # Создаем требуемые метрики
                metrics[worker].append(ZabbixMetric(worker, 'miner.pool.status', 1))
                metrics[worker].append(ZabbixMetric(worker, 'miner.pool.hashrate', poolWorkersHashrate[worker.lower()]))
            else:
                metrics[worker].append(ZabbixMetric(worker, 'miner.pool.status', 0))
        return metrics

    @staticmethod
    def __nanoPool(workers, data):
        metrics = {}
        # Если статус в ответе от пула отрицательный
        if not data['status']:
            for worker in workers:
                metrics[worker] = [ZabbixMetric(worker, 'pool.status', 1), ]
                metrics[worker].append(ZabbixMetric(worker, 'pool.answer.status', 0))
            return metrics

        # Hashrate майнеров на пуле
        poolWorkersHashrate = {item['worker']: item['hashrate'] for item in data['data']}
        # Для каждого ожидаемого на пуле майнера
        for worker in workers:
            # Статус пула
            metrics[worker] = [ZabbixMetric(worker, 'pool.status', 1), ]
            metrics[worker].append(ZabbixMetric(worker, 'pool.answer.status', 1))
            # Если отсутствует на пуле
            if worker not in poolWorkersHashrate:
                metrics[worker].append(ZabbixMetric(worker, 'miner.pool.status', 0))
            else:
                # Создаем требуемые метрики
                metrics[worker].append(ZabbixMetric(worker, 'miner.pool.status', 1))
                metrics[worker].append(ZabbixMetric(worker, 'miner.pool.hashrate', poolWorkersHashrate[worker]))
        return metrics


def main():
    """Выполняется если скрипт запущен явно а не подключен как модуль.
       В соответвии файлом настроек опрашивает пулы. Отправляет данные
       на Zabbix сервер."""

    # Загружаем конфигурацию
    config = ConfigParser()

    # Отключение трассировки
    if not config.script.debug:
        sys.tracebacklimit = None

    # Опрашиваем пулы
    pools = Sender(config.pools)
    pools.sendRequests()

    # Отправляем собранные данные Zabbix серверу
    if config.zabbix.send:
        zabbix = Zabbix(pools.union, config.zabbix.server, config.zabbix.port, config.zabbix.log)
        zabbix.send()

    return 0


# Если скрипт запущен явно а не подключен как модуль
if __name__ == "__main__":
    sys.exit(main())
