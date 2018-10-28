#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import django
import json
import logging
import os
import re
import socket
import sys

from collections import namedtuple
from copy import deepcopy
from ipaddress import ip_address
from pyzabbix import ZabbixMetric, ZabbixSender
from systemd import journal

from pyminers import Sender


class Worker():
    """Извлекает настроки опроса майнеров
    и отправки статистики Zabbix из БД Django.
    Сохраняет результаты опроса в БД.
    """

    def __init__(self, config='Default'):
        # Получаем общие настройки, как словарь
        self.__config = Config.objects.filter(
            name=config,
            enabled=True,
        ).values().first()
        if not self.__config:
            # Конфигурация должна существовать
            # и быть включена
            raise ValueError(
                "Config \"{config}\" does not"
                " exists or disabled".format(
                    config=config,
                )
            )

        # Инициализация логирования
        if self.config.log == 'FI':
            self.log = self.config.log_file
        else:
            self.log = self.config.log

        # Получаем настроки опроса майнеров
        self.__server_tasks = ServerTask.objects.filter(enabled=True)
        if not self.__server_tasks:
            raise ValueError(
                "Tasks do not exists, check"
                " miners request settings"
            )

    @property
    def config(self):
        """Общие настроки
        """
        try:
            properties = namedtuple(
                'config',
                [item.lower() for item in self.__config.keys()],
            )
            return properties(*self.__config.values())
        except AttributeError:
            return None

    @property
    def tasks(self):
        """Параметры опроса майнеров
        """
        tasks = {}

        # Соответствие между именами майнеров
        # из pyminers и майнерами из БД django
        miner_name_map = {
            "antminer-s9-cgminer-490": "CGMiner",
            "claymores-cryptonote-gpu-97": "Monero",
            "claymores-dual-ethereum-amd-gpu-98": "Etherium",
            "ewbfs-cuda-zcash-034b": "ZCash",
        }

        # Формируем список заданий для Sender
        for task in self.__server_tasks:
            task_miner = miner_name_map.get(task.server.miner.slug, 'Miner')
            tasks[task.id] = {
                'Host': task.server.host,
                'Port': task.server.port,
                'Miner': task_miner,
                'Timeout': task.timeout,
                'Request': [request.request for request in task.requests.all()]
            }
            if task_miner == 'Miner':
                self.log.warning(
                    "Задан опрос неизвестного майнера '{miner}',"
                    " задание '{task}'. Обработка полей"
                    " запрос/ответ выполнена не будет.".format(
                        miner=task.server.miner,
                        task=task.id,
                    ),
                )
        return tasks

    @property
    def log(self):
        """log: логирование результатов работы"""
        try:
            return self.__logger
        except AttributeError:
            return None

    @log.setter
    def log(self, value):
        """log: логирование результатов работы
        """

        journalName = 'minigstatistic'

        timeformat = "%Y.%m.%d-%H:%M:%S"

        self.__logger = logging.getLogger(journalName)
        self.__logger.setLevel(logging.INFO)

        if value == 'NO':
            # Не вести лог
            handler = logging.NullHandler()
            formatter = logging.Formatter()
        elif value == 'SY':
            # Запись лога в системный журнал
            handler = journal.JournaldLogHandler(identifier=journalName)
            formatter = logging.Formatter('%(levelname)s: %(message)s')
        elif value == 'ST':
            # Вывод лога в stdout
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '[%(asctime)s] %(name)s: %(levelname)s: %(message)s',
                timeformat,
            )
        else:
            # Запись лога в файл
            handler = logging.FileHandler(value)
            formatter = logging.Formatter(
                '[%(asctime)s] %(name)s: %(levelname)s: %(message)s',
                timeformat,
            )

        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        self.__logger.addHandler(handler)

    def get_server_names(self):
        """Возвращает словарь {task.id: server.name, }
        """
        return {task.id: task.server.name for task in self.__server_tasks}

    def save(self, data):
        """Добавляет результаты выполнения заданий в БД
        """
        # Представляет ответ от майнера в требуемом формате
        convert = Converter()

        # Получаем идентификатор опроса
        if ServerStatistic.objects.count():
            # Есть записи в таблице
            request_id = ServerStatistic.objects.aggregate(
                Max('request_id'),
            )['request_id__max'] + 1
        else:
            request_id = 1

        # Добавяем результаты выполнения заданий
        for task_id, task_data in data.items():
            task = ServerTask.objects.get(id=task_id)
            # Готовим данные для добавения
            data = {
                # Идентификатор задания
                'task': task.id,
                # Идентификатор опроса
                'request_id': request_id,
                # True, если все запросы успешны
                'status': all(
                    [not line['Error']
                     for line in task_data['Exchange']],
                ),
                # Время выполнения последнего запроса
                'executed': max(
                    [line['When']
                     for line in task_data['Exchange']],
                ),
                # Результаты запросов
                'result': dict(),
            }

            # Добавляем результаты запросов
            for line in task_data['Exchange']:
                if line['Error']:
                    # Если любой из запросов завершился ошибкой
                    # добавляем только ответ с описанием ошибки
                    data['result'] = line['Response']
                    break
                for request in task.requests.values('name', 'request'):
                    # Определяем имя запроса по телу запроса из ответа
                    if line['Request'] == json.loads(request['request']):
                        # Добавляем в виде {'RequestName': Response, }
                        data['result'][request['name']] = line['Response']
                        break

            # Если запрос не завершился ошибкой
            # преобразуем результаты к требуемому формату
            if data['status']:
                data['result'] = convert(
                    task.server.miner.slug,
                    data['result'],
                )

            # Форма ожидает строку а не объект
            data['result'] = json.dumps(data['result'])

            # Форма обеспечивает проверку данных
            form = ServerStatisticForm(data)

            if form.is_valid():
                # Сохраняем результаты в БД
                form.save()

                # Обновляем статус задания
                task.executed = form.instance.executed
                task.status = form.instance.status
                task.save()

                # Запись в лог
                self.log.info(
                    "Сохранение в БД:  Задание: '{data}'".format(
                        data=form.instance,
                    ),
                )
            else:
                # Запись в лог
                self.log.error(
                    "Ошибка записи  в БД: Задание: '{data}'"
                    " Причина: {error}".format(
                        data=form.instance,
                        error=(form.errors, ),
                    ),
                )


class Converter():
    """Приводит ответы от майнеров к требуемому формату
    """

    def __init__(self):
        # Методы для преобразования ответов майнеров
        self.__supported_miners = {
            "antminer-s9-cgminer-490": self.__cGMiner,
            "claymores-cryptonote-gpu-97": self.__etherium,
            "claymores-dual-ethereum-amd-gpu-98": self.__etherium,
            "ewbfs-cuda-zcash-034b": self.__zCash,
        }

    def __call__(self, miner, data):
        """Приводит ответы от майнеров к требуемому формату
        """
        if miner in self.miners:
            return self.__supported_miners[miner](data)
        else:
            return data

    @property
    def miners(self):
        """Поддерживаемые майнеры"""
        return self.__supported_miners.keys()

    @staticmethod
    def __cGMiner(value):
        """Модифицирует ответ от сервера CGMiner
        """
        try:
            summary = deepcopy(value['Summary']['SUMMARY'][0])
            stats = deepcopy(value['Stats']['STATS'][0])
        except KeyError as e:
            raise ValueError("Invalid response:", e) from None

        # Uptime
        summary['Elapsed'] = str(datetime.timedelta(seconds=summary['Elapsed']))

        # Last getwork
        summary['Last getwork'] = datetime.datetime.fromtimestamp(
            summary['Last getwork'],
        ).strftime("%Y.%m.%d-%H:%M:%S")

        # Шаблоны поиска
        templates = {
            'Fans': '^fan[0-9]+$',
            'Temps 1': '^temp[0-9]+$',
            'Temps 2': '^temp2_[0-9]+$',
            'Temps 3': '^temp3_[0-9]+$',
            'Freq av': '^freq_avg[0-9]+$',
            'Chainrate': '^chain_rateideal[0-9]+$',
        }
        templates = {key: re.compile(item) for key, item in templates.items()}

        # Ищем поля по шаблону и объединяем данные
        summary.update(
            {key: ', '.join(
                [str(item)
                 for _, item in stats.items()
                 if bool(template.match(_)) and item])
             for key, template in templates.items()},
        )

        # Description
        summary['Description'] = '{miner} - {version}'.format(
            miner=stats['Type'],
            version=stats['Miner'],
        )

        summary['Dev/Pool Rejected (%)'] = '{dev} / {pool}'.format(
            dev=summary['Device Rejected%'],
            pool=summary['Pool Rejected%'],
        )

        # Переименовываем и возвращаем только необходимые поля
        return {val: summary[key] for key, val in {
            'Elapsed': 'elapsed',
            'Accepted': 'accepted',
            'Rejected': 'rejected',
            'GHS av': 'ghs_av',
            'Hardware Errors': 'hardware_errors',
            'Discarded': 'discarded',
            'Dev/Pool Rejected (%)': 'dev_pool_rejected',
            'Last getwork': 'last_getwork',
            'Fans': 'fans',
            'Temps 1': 'temps_1',
            'Temps 2': 'temps_2',
            'Description': 'description'}.items()}

    @staticmethod
    def __zCash(value):
        """Модифицирует ответ от сервера ZCash
        """
        try:
            value = deepcopy(value['Statistic'])
        except KeyError as e:
            raise ValueError("Invalid response:", e) from None

        # Расшифровка статусов состояния GPU
        gpuStatus = {
            0: 'launched',
            1: 'prepare',
            2: 'work',
            3: 'stopped'
        }

        """Ответ от сервера приходит в виде списка словарей,
        где каждый словарь - статистика работы по одному GPU
        """

        # Преобразуем список слоарей в словарь со списками
        value = dict(zip(value[0], zip(*[item.values() for item in value])))
        # Расшифровываем статусы GPU
        value['gpu_status'] = [gpuStatus[item] for item in value['gpu_status']]
        # Преобразуем списки в строки значений разделенные ';'
        value = {key: '; '.join([str(item) for item in value[key]])
                 for key in value}
        # Возвращаем только необходимые поля
        return {key: value[key] for key, val in [
            'gpu_status', 'temperature', 'gpu_power_usage',
            'speed_sps', 'accepted_shares', 'rejected_shares',
        ]}

    @staticmethod
    def __etherium(value):
        """Модифицирует ответ от сервера Etherium
        """
        try:
            value = deepcopy(value['Statistic'])
        except KeyError as e:
            raise ValueError("Invalid response:", e) from None

        # Uptime
        value['Uptime'] = str(datetime.timedelta(minutes=value['Uptime']))

        # Статистика ETH / DCR
        for key in ['ETH', 'DCR']:
            try:
                percent = round(
                    value[key]['Rejected'] * 100 / value[key]['Shares'], 2
                )
            except ZeroDivisionError:
                percent = 0

            value[key] = '{T} GH/s, {A}/{R} ({P}%)'.format(
                T=value[key]['Hashrate'] / 1000,
                A=value[key]['Shares'],
                R=value[key]['Rejected'],
                P=percent,
            )

        value['ETH / GPU'] = '; '.join(
            [str(item) for item in value['ETH Detailed']]
        )
        value['DCR / GPU'] = '; '.join(
            [str(item) for item in value['DCR Detailed']]
        )

        # Параметры GPU
        value['GPU'] = ' '.join(
            ['({T}C:{S}%)'.format(
                T=item[0],
                S=item[1])
             for item in zip(
                 value['GPU']['Temperatures'],
                 value['GPU']['Fan Speeds'],)
             ]
        )

        # Информация по pool'ам
        value['Pools'] = ' '.join(
            ['{A}:{P}'.format(
                A=item['Host'],
                P=item['Port'])
             for item in value['Pools']]
        )

        # Переименовываем и возвращаем только необходимые поля
        return {val: value[key]
                for key, val in {
                    'Uptime': 'uptime',
                    'ETH': 'eth',
                    'ETH / GPU': 'eth_per_gpu',
                    'DCR': 'dcr',
                    'DCR / GPU': 'dcr_per_gpu',
                    'GPU': 'gpu',
                    'Pools': 'pools'}.items()
                }


class Zabbix():
    """Отправляет статистику работы майнеров на Zabbix серввер"""

    def __init__(self, miners, server='127.0.0.1',
                 port=10051, timeout=5, log='False'):
        """Аргументы:
           miners: результаты опроса майнеров, в формате dict
           с параметрами запросов и полученными ответами:
               {'id': {'Host': str, 'Port': int, 'Miner': str,
                       'Exchange':[{'Request': str, 'Response': dict,
                                    'Error': bool}, ],
                       'Description': str }, }
               где:
                   id - netbios имя имя хоста или другой идентификатор
                   Host - ip адрес хоста
                   Port - порт майнера
                   Miner - тип майнера
                   Exchange - список запросов и ответов майнеров:
                       Request - тип запроса
                       Result - ответ от майнера
                       Error - флаг успешности запроса
                   Description - описание хоста (необязательное поле)

           server: адрес сервера
           port: порт сервера
           log: логирование результатов работы, может принимать значения:
               False - не вести лог
               log - экземпляр logging.Logger
               system - записть в системный лог systemd
               stdout - вывод в стандартный поток
               или принимает имя файла для записи лога
        """

        self.__supportedMiners = {
            'CGMiner': self.__cGMiner,
            'ZCash': self.__zCash,
            'Monero': self.__etherium,
            'Etherium': self.__etherium
        }

        self.miners = deepcopy(miners)
        self.server = server
        self.port = port
        self.timeout = timeout
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
            raise ValueError(
                "server = {message}".format(message=e),
            ) from None

        if address.is_private:
            self.__server = value
        else:
            raise ValueError(
                "server = '{address}' address does "
                "not appear to be in private network".format(
                    address=address,
                ),
            )

    @property
    def port(self):
        """Порт сервера"""
        try:
            return self.__port
        except AttributeError:
            return None

    @port.setter
    def port(self, value):
        """Порт сервера, должен находится в
        передлах от 1  до 65535 и быть целым числом
        """
        if value in range(1, 65536):
            self.__port = value
        else:
            raise ValueError(
                "port = '{port}' port must be "
                "in range 1..65535".format(port=value),
            )

    @property
    def timeout(self):
        """Время ожидани ответа Zabbix"""
        try:
            return self.__timeout
        except AttributeError:
            return None

    @timeout.setter
    def timeout(self, value):
        """Время ожидани ответа Zabbix, должно быть в
        пределах от 1 до 60 и быть целым
        """
        if value in range(1, 61):
            self.__timeout = value
            self.__error = False
        else:
            raise ValueError(
                "Zabbix response timeout '{timeout}'"
                " must be in range 1..60".format(timeout=value),
            )

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
        log - экземпляр logging.Logger
        system - записть в системный лог systemd
        stdout - вывод в стандартный поток
        или принимает имя файла для записи лога
        """

        if isinstance(value, logging.Logger):
            self.__logger = value
            return None

        journalName = 'minigstatistic'

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
            formatter = logging.Formatter(
                '[%(asctime)s] %(name)s: %(levelname)s: %(message)s',
                timeformat,
            )
        else:
            # Запись лога в файл
            handler = logging.FileHandler(value)
            formatter = logging.Formatter(
                '[%(asctime)s] %(name)s: %(levelname)s: %(message)s',
                timeformat,
            )

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
        """Отправляет статистику работы майнеров на серввер"""

        for name, metrics in self.__metrics.items():
            server = ZabbixSender(
                self.server,
                self.port,
                chunk_size=len(metrics),
            )
            try:
                self.log.info(
                    "metrics sended to {server}:{port} "
                    "for {miner} ({result})".format(
                        server=self.server,
                        port=self.port,
                        miner=name,
                        result=server.send(metrics),
                    ),
                )
            except socket.error as e:
                self.log.error(
                    "error on sending metrics to {server}:{port} "
                    "for {miner} ({message})".format(
                        server=self.server,
                        port=self.port,
                        miner=name, message=e,
                    ),
                )
                break

    def __createMetrics(self):
        """Формирует метрики для отправки статистики на сервер"""
        self.__metrics = {}

        for name, data in self.miners.items():
            # Ищем ошибки
            errorResponses = [
                item['Response']
                for item in data['Exchange']
                if item['Error']]
            # Если при получении статистики работы майнера произошла ошибка
            if errorResponses:
                # Создаем соответвующую метрику
                self.__metrics[name] = [ZabbixMetric(
                    name,
                    'miner.status', 0), ]
                # Записываем сообщение в лог
                self.log.error(
                    "error in request for miner {name} at "
                    "{host}:{port} ({message})".format(
                        name=name,
                        host=data['Host'],
                        port=data['Port'],
                        message=errorResponses[0],
                    ),
                )
            else:
                # Создаем все метрики для майнера
                self.__metrics[name] = [
                    ZabbixMetric(name, key, value)
                    for key, value in
                    self.__supportedMiners[data['Miner']](data['Exchange'])]

    @staticmethod
    def __cGMiner(value):

        # К маинеру делается два запроса. В зависимости от
        # того какой ответ попал в список первым назначаем переменные
        if 'SUMMARY' in value[0]['Response']:
            summary = deepcopy(value[0]['Response']['SUMMARY'][0])
            stats = deepcopy(value[1]['Response']['STATS'][0])
        else:
            summary = deepcopy(value[1]['Response']['SUMMARY'][0])
            stats = deepcopy(value[0]['Response']['STATS'][0])

        metric = {}
        metric['miner.status'] = 1
        metric['miner.version'] = stats['miner_version']
        metric['miner.uptime'] = summary['Elapsed']
        metric['miner.shares'] = summary['Accepted']
        metric['miner.shares.rejected'] = summary['Rejected']
        metric['miner.hashrate.average'] = summary['GHS av']
        metric['miner.lastgetwork'] = summary['Last getwork']
        metric['miner.temperature.max'] = stats['temp_max']
        metric['miner.acn.total'] = stats['total_acn']
        metric['miner.fan.number'] = stats['fan_num']

        template = re.compile('^fan[0-9]+$')
        speed = [item for _, item in stats.items()
                 if bool(template.match(_)) and item]
        metric['miner.fan.discovery'] = json.dumps({
            'data': [{'{#FANID}': str(num)}
                     for num in range(metric['miner.fan.number'])]})

        for num, item in enumerate(speed):
            metric['miner.fan.speed[{fan}]'.format(fan=num)] = speed[num]

        return metric.items()

    @staticmethod
    def __zCash(value):
        value = value[0]['Response']

        metric = {}
        metric['miner.status'] = 1
        metric['miner.gpu.number'] = len(value)
        metric['miner.shares'] = sum(
            [item['accepted_shares'] for item in value])
        metric['miner.shares.rejected'] = sum(
            [item['rejected_shares'] for item in value])
        try:
            metric['miner.shares.rejected.percent'] = round(
                metric['miner.shares.rejected'] * 100 / metric['miner.shares'], 4)
        except ZeroDivisionError:
            metric['miner.shares.rejected.percent'] = float(0)

        metric['miner.gpu.discovery'] = json.dumps(
            {'data': [{'{#GPUID}': str(num)}
                      for num in range(metric['miner.gpu.number'])]}
        )

        for num, item in enumerate(value):
            metric['miner.gpu.status[{gpu}]'.format(
                gpu=num)] = item['gpu_status']
            metric['miner.gpu.shares[{gpu}]'.format(
                gpu=num)] = item['accepted_shares']
            metric['miner.gpu.shares.rejected[{gpu}]'.format(
                gpu=num)] = item['rejected_shares']
            metric['miner.gpu.speed[{gpu}]'.format(
                gpu=num)] = item['speed_sps']
            metric['miner.gpu.powerusage[{gpu}]'.format(
                gpu=num)] = item['gpu_power_usage']
            metric['miner.gpu.temperature[{gpu}]'.format(
                gpu=num)] = item['temperature']

        return metric.items()

    @staticmethod
    def __etherium(value):
        value = value[0]['Response']

        metric = {}
        metric['miner.status'] = 1
        metric['miner.uptime'] = value['Uptime'] * 60
        metric['miner.version'] = '{type}-{version}'.format(
            type=value['Version']['Type'],
            version=value['Version']['Number'],
        )

        metric['miner.eth.hashrate'] = value['ETH']['Hashrate'] * 10**6
        metric['miner.eth.shares'] = value['ETH']['Shares']
        metric['miner.eth.shares.rejected'] = value['ETH']['Rejected']
        try:
            metric['miner.eth.shares.rejected.percent'] = round(
                metric['miner.eth.shares.rejected'] * 100 / metric['miner.eth.shares'], 4)
        except ZeroDivisionError:
            metric['miner.eth.shares.rejected.percent'] = float(0)

        metric['miner.dcr.hashrate'] = value['DCR']['Hashrate'] * 10**6
        metric['miner.dcr.shares'] = value['DCR']['Shares']
        metric['miner.dcr.shares.rejected'] = value['DCR']['Rejected']
        try:
            metric['miner.dcr.shares.rejected.percent'] = round(
                metric['miner.dcr.shares.rejected'] * 100 / metric['miner.dcr.shares'], 4)
        except ZeroDivisionError:
            metric['miner.dcr.shares.rejected.percent'] = float(0)

        metric['miner.gpu.number'] = len(value['ETH Detailed'])
        metric['miner.gpu.discovery'] = json.dumps(
            {'data': [{'{#GPUID}': str(num)}
                      for num in range(metric['miner.gpu.number'])]}
        )

        for index, item in enumerate(value['ETH Detailed']):
            if not isinstance(item, int):
                value['ETH Detailed'][index] = 0

        for index, item in enumerate(value['DCR Detailed']):
            if not isinstance(item, int):
                value['DCR Detailed'][index] = 0

        for num, _ in enumerate(value['ETH Detailed']):
            metric['miner.gpu.dcr.hashrate[{gpu}]'.format(
                gpu=num)] = value['DCR Detailed'][num] * 10**6
            metric['miner.gpu.eth.hashrate[{gpu}]'.format(
                gpu=num)] = value['ETH Detailed'][num] * 10**6
            metric['miner.gpu.fspeed[{gpu}]'.format(
                gpu=num)] = value['GPU']['Fan Speeds'][num]
            metric['miner.gpu.temperature[{gpu}]'.format(
                gpu=num)] = value['GPU']['Temperatures'][num]
        return metric.items()


def main():
    # Загружаем задания из БД
    works = Worker(config='Develop')

    # Опрашиваем майнеры
    sender = Sender(works.tasks)
    sender.sendRequests()

    # Добавление результатов в БД
    works.save(sender.results)

    # Отправляем собранные данные Zabbix серверу
    if works.config.zabbix_send:
        # Меняем ID задания на имя сервера
        server_names = works.get_server_names()
        zabbix_data = {server_names[key]: value
                       for key, value in sender.union.items()}

        zabbix = Zabbix(
            zabbix_data,
            works.config.zabbix_server,
            works.config.zabbix_port,
            works.config.zabbix_timeout,
            works.log,
        )
        zabbix.send()


if __name__ == '__main__':

    # Текущая директория
    PROJECT_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

    # Имя проекта django
    DJANGO_PROJECT_NAME = 'miningstatistic'

    # Если проект лежит рядом (или добавляем
    # абсолютный путь к файлам проекта)
    sys.path.append(os.path.join(PROJECT_DIR, DJANGO_PROJECT_NAME))

    # Добавляем в окружение переменную с настройками проекта
    # как правило 'projectname.settings'
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        DJANGO_PROJECT_NAME + ".settings",
    )

    # Настройка окружения
    django.setup()

    # Здесь импортируем модули проекта
    from task.models import Config, ServerTask
    from statistic.models import ServerStatistic
    from statistic.forms import ServerStatisticForm
    from django.db.models import Max

    sys.exit(main())
