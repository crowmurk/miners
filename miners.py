#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Скрипт опроса майнеров.

Читает из конфигурационного файла параметры опроса майнеров,
опрашивает их, отпраляет полученную статистику работы майнеров
на Zabbix сервер.  Может работать как cgi скрипт
(представляя статистику в виде таблиц)
"""

__version__ = "2.6.0"
__author__ = "varga"

import json
import logging
import os
import re
import socket
import sys

from collections import namedtuple
from copy import deepcopy
from datetime import datetime
from ipaddress import ip_address
from string import Template

from configobj import ConfigObj, ConfigObjError
from configobj import flatten_errors, get_extra_values
from json2html import json2html
from pyzabbix import ZabbixMetric, ZabbixSender
from systemd import journal
from validate import Validator

from pyminers import Sender


class ConfigParser():
    """Загружает настройки для работы скрипта"""

    def __init__(self, config='miners.conf'):
        """Аргументы:
        config: путь к файлу конфигурации
        """

        # Шаблон файла конфигурации
        template = """
        [Script]
            Template = string(default=miners.template.html)
            Refresh = integer(min=10, max=3600, default=30)
            Url = string(default=cgi-bin/miners.py/)
            Colorize = boolean(default=False)
            Debug = boolean(default=False)
        [Zabbix]
            Server = ip_addr(default=127.0.0.1)
            Port = integer(default=10051)
            Log = string(default=False)
            Send = boolean(default=False)
        [__many__]
            Host = ip_addr
            Port = integer(min=1, max=65535)
            Miner = string
            Request = force_list
            Timeout= integer(min=1, max=60, default=5)
            Description = string
        """

        # Загружаем конфигурацию
        try:
            self.__config = ConfigObj(
                config,
                configspec=template.split('\n'),
                file_error=True,
            )
        except (ConfigObjError, IOError) as e:
            # Ошибка загрузки конфигурации
            raise IOError(
                "could not read config file'{file}': {error}".format(
                    file=config, error=e,
                ),
            ) from None

        # Проверяем файл конфигурации
        validator = Validator()
        result = self.__config.validate(validator, preserve_errors=True)

        # Если возникли ошибки
        if result is not True:
            for (sections, key, result) in flatten_errors(self.__config, result):
                if key is not None:
                    if key != 'Description':
                        raise ValueError(
                            "the key '{key}' in the section '{section}' "
                            "of config file failed validation: "
                            "{result}".format(
                                key=key,
                                section=', '.join(sections),
                                result=result if result else "missing key",
                            ),
                        )
                else:
                    raise ValueError(
                        "the following section in "
                        "config file was missing: '{section}'".format(
                            section=', '.join(sections),
                        ),
                    )

        # Проверяем на наличие дополнительных параметров
        for section, key in get_extra_values(self.__config):
            raise ValueError(
                "extra section or key '{key}' "
                "in section '{section}' of config file".format(
                    key=key,
                    section=', '.join(section) if section else None,
                ),
            )

    @property
    def script(self):
        """Параметры работы скрипта,
        представлены как свойства объекта
        """
        try:
            properties = namedtuple(
                'script',
                [item.lower() for item in self.__config['Script'].keys()],
            )
            return properties(*self.__config['Script'].values())
        except AttributeError:
            return None

    @property
    def zabbix(self):
        """Параметры Zabbix сервера,
        представлены как свойства объекта
        """
        try:
            properties = namedtuple(
                'zabbix',
                [item.lower() for item in self.__config['Zabbix'].keys()],
            )
            return properties(*self.__config['Zabbix'].values())
        except AttributeError:
            return None

    @property
    def miners(self):
        """Список параметров опроса майненров в формате dict"""
        try:
            return {item: value
                    for item, value in self.__config.items()
                    if item not in ['Script', 'Zabbix']}
        except AttributeError:
            return None


class HtmlPage():
    """Создает html страницу с результатами опроса майнеров"""

    def __init__(self, miners, template, refresh=30, url='', colorize=False):
        """Аргументы:
        miners: результаты опроса майнеров, в формате dict
        с параметрами запросов и полученными ответами:
            {'id': {'Host': str, 'Port': int, 'Miner': str,
                    'Exchange':[{'Request': str,
                                 'Response': dict,
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

        refresh: интервал обновления страницы
        url: относительная ссылка на скрипт
        colorize: флаг включения подсветки критическких значений
        """

        self.__supportedMiners = {
            'CGMiner': self.__cGMiner,
            'ZCash': self.__zCash,
            'Monero': self.__etherium,
            'Etherium': self.__etherium,
        }

        self.__results = {item: {'statistic': [], 'errors': []}
                          for item in self.supportedMiners}

        self.miners = deepcopy(miners)
        self.template = template
        self.refresh = refresh
        self.url = url
        self.colorize = colorize

    @property
    def supportedMiners(self):
        """Поддерживаемые майнеры"""
        return self.__supportedMiners.keys()

    @property
    def refresh(self):
        """Интервал обновления страницы"""
        try:
            return self.__refresh
        except AttributeError:
            return None

    @refresh.setter
    def refresh(self, value):
        """Интервал обновления страницы, должен находится
        в передлах от 1  до 3600 и быть целым числом
        """
        if value in range(10, 3601):
            self.__refresh = value
        else:
            raise ValueError(
                "refresh = '{refresh}' refresh must be "
                "in range 10..3600".format(refresh=value),
            )

    @property
    def url(self):
        """Относительная ссылка на скрипт"""
        try:
            return self.__url
        except AttributeError:
            return None

    @url.setter
    def url(self, value):
        """Относительная ссылка на скрипт,
        должна быть строкой ненулевой длины
        """
        if isinstance(value, str) and value:
            self.__url = value
        else:
            raise ValueError(
                "url = '{url}' script url must be sting".format(url=value),
            )

    @property
    def colorize(self):
        """Флаг включения подсветки критическких значений
        параметров работы майнера
        """
        try:
            return self.__colorize
        except AttributeError:
            return None

    @colorize.setter
    def colorize(self, value):
        """Флаг включения подсветки критическких значений
        параметров работы майнера, должен быть True или False
        """
        if isinstance(value, bool):
            self.__colorize = value
        else:
            raise ValueError(
                "colorize = '{colorize}' flag must be "
                "boolean type".format(colorize=value),
            )

    def createTables(self):
        """Создает html таблицы c результатами опроса майнеров"""
        for name, data in self.miners.items():
            # Формируем результат
            line = {
                'Server': "{name} - {host}:{port}".format(
                    name=name,
                    host=data['Host'],
                    port=data['Port'],
                ),
            }
            # Ищем ошибки
            errorResponses = [item['Response']
                              for item in data['Exchange'] if item['Error']]
            # Преобразуем ответ от майнера
            line.update(
                errorResponses[0] if errorResponses else
                self.__supportedMiners[data['Miner']](data['Exchange']),
            )
            # Добавляем описание из результатов
            # опроса или конфигурационного файла
            line['Description'] = data.get(
                'Description',
                line.get('Description', ''),
            )
            # Добавляем
            self.__results[data['Miner']]['errors' if errorResponses else
                                          'statistic'].append(line)

        # Преобразуем в html
        self.__results = {
            minerType: {
                resultsType: json2html.convert(json=results)
                for resultsType, results in type.items() if results}
            for minerType, type in self.__results.items()}

        # Шаблон html для вывода таблиц с результатами опроса
        table = """
            <table>
                <tr>
                    <th style="background-color: LIGHTGOLDENRODYELLOW">
                        {miner} {type}:
                    </th>
                <tr>
            </table>
            <br>
            {table}
        """

        # Содединяем таблицы
        self.__results = '<br>\n\t'.join(
            table.format(
                miner=minerType,
                type=resultsType,
                table=results,
            )
            for minerType, type in self.__results.items()
            for resultsType, results in type.items() if results
        )

    @staticmethod
    def __cGMiner(value):
        """Модифицирует ответ от сервера CGMiner
        для удобства представления в виде html таблицы
        """

        # К маинеру делается два запроса. В зависимости от
        # того какой ответ попал в список первым назначаем переменные
        if 'SUMMARY' in value[0]['Response']:
            summary = deepcopy(value[0]['Response']['SUMMARY'][0])
            stats = deepcopy(value[1]['Response']['STATS'][0])
        else:
            summary = deepcopy(value[1]['Response']['SUMMARY'][0])
            stats = deepcopy(value[0]['Response']['STATS'][0])

        # Обработка ответа
        # Elapsed time
        m, _ = divmod(summary['Elapsed'], 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        summary['Elapsed'] = '{}d {:02}:{:02}'.format(d, h, m)

        summary['Last getwork'] = datetime.fromtimestamp(
            summary['Last getwork'],
        )

        # Обработка ответа
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

        summary['Description'] = '{miner} - {version}'.format(
            miner=stats['Type'],
            version=stats['Miner'],
        )

        return {key: summary[key]
                for key in [
                    'Elapsed', 'Accepted', 'Rejected',
                    'GHS av', 'Hardware Errors', 'Discarded',
                    'Device Rejected%', 'Pool Rejected%',
                    'Last getwork', 'Fans', 'Temps 1',
                    'Temps 2', 'Description']
                }

    @staticmethod
    def __zCash(value):
        """Модифицирует ответ от сервера ZCash
        для удобства представления в виде html таблицы
        """

        value = deepcopy(value[0]['Response'])

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
        # Переименовываем и возвращаем только необходимые поля
        return {val: value[key]
                for key, val in {
                    'gpu_status': 'GPU status',
                    'temperature': 'Temperatures',
                    'gpu_power_usage': 'GPU power usage',
                    'speed_sps': 'Solution / second',
                    'accepted_shares': 'Accepted shares',
                    'rejected_shares': 'Rejected shares'}.items()
                }

    @staticmethod
    def __etherium(value):
        """Модифицирует ответ от сервера Etherium
        для удобства представления в виде html таблицы
        """

        value = deepcopy(value[0]['Response'])

        # Uptime
        h, m = divmod(value['Uptime'], 60)
        d, h = divmod(h, 24)
        value['Uptime'] = '{}d {:02}:{:02}'.format(d, h, m)
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
        # Возвращаем только необходимые поля, в указанном порядке
        return {key: value[key]
                for key in [
                    'Uptime', 'ETH', 'ETH / GPU',
                    'DCR', 'DCR / GPU', 'GPU', 'Pools']
                }

    def __str__(self):
        """Формирует html страницу"""
        currentTime = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        # Загружаем шаблон из файла
        with open(self.template, 'r') as file:
            template = Template(file.read())
            # Подставляем значения
            return template.substitute(
                tables=self.__results,
                currentTime=currentTime,
                refresh=self.refresh,
                url=self.url,
                version=__version__,
            )


class Zabbix():
    """Отправляет статистику работы майнеров на Zabbix серввер"""

    def __init__(self, miners, server='127.0.0.1',
                 port=10051, log='False'):
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
        или принимает имя файла для записи лога
        """

        if __name__ == "__main__":
            journalName = os.path.basename(__file__)
        else:
            journalName = __name__

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
            "data": [{"{#FANID}": str(num)}
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
            {"data": [{"{#GPUID}": str(num)}
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
            {"data": [{"{#GPUID}": str(num)}
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
    """Выполняется если скрипт запущен явно а не подключен как модуль.
    В соответвии файлом настроек опрашивает майнеры. Предназначен
    для работы как cgi сценарий или отправки данных на Zabbix сервер.
    """

    # Загружаем конфигурацию
    config = ConfigParser()

    # Отключение трассировки
    if not config.script.debug:
        sys.tracebacklimit = None

    # Опрашиваем майнеры
    miners = Sender(config.miners)
    miners.sendRequests()

    # Отправляем собранные данные Zabbix серверу
    if config.zabbix.send:
        zabbix = Zabbix(
            miners.union,
            config.zabbix.server,
            config.zabbix.port,
            config.zabbix.log,
        )
        zabbix.send()
        return 0

    # Создаем html страницу
    page = HtmlPage(
        miners.union,
        template=config.script.template,
        refresh=config.script.refresh,
        url=config.script.url,
        colorize=config.script.colorize,
    )
    page.createTables()

    # Если скрипт запущен как cgi
    if 'REQUEST_METHOD' in os.environ:
        print(page)
        return 0

    # Иначе создаем файл для просмотра результатов работы
    filename = './index.html'
    with open(filename, 'w') as file:
        file.write('{}'.format(page))
    return 0


# Если скрипт запущен явно а не подключен как модуль
if __name__ == "__main__":
    sys.exit(main())
