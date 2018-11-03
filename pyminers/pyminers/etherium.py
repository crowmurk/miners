# -*- coding: utf-8 -*-

"""Модуль содержит реализацию класса Etherium"""

import json
from re import split

from validictory import validate

from .miner import Miner


class Etherium(Miner):
    """Отправляет запросы к майнеру Etherium"""

    def __init__(self, host='127.0.0.1', port=3333,
                 request='Statistic', timeout=5, gpu=None):
        """Аргументы:
        host: адрес сервера
        port: порт майнера
        request: тип запроса
            Поддерживаемые запросы (Statistic, Restart, Reboot, GPU)
        timeout: время ожидани ответа сервера
        """

        # Поддерживаемые запросы
        self.__requests = {
            'Statistic': {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "miner_getstat1",
            },
            'Restart': {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "miner_restart",
            },
            'Reboot': {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "miner_reboot",
            },
            'GPU': {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "control_gpu",
                "params": gpu,
            },
        }

        # Шаблон для проверки ответов
        self.__templates = {
            'Statistic': {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "error": {"type": "null"},
                    "result": {
                        "items": {"type": "string"},
                        "minItems": 9,
                        "maxItems": 9,
                    },
                },
            },
            'Restart': None,
            'Reboot': None,
            'GPU': None,
        }

        self.host = host
        self.port = port
        self.timeout = timeout
        self.request = request

    @property
    def requests(self):
        """Поддерживаемые запросы"""
        return self.__requests.keys()

    @property
    def request(self):
        """Запрос к серверу в формате dict
        """
        return super().request

    @request.setter
    def request(self, value):
        """Запрос к серверу, должен соответсвовать API
        """
        if isinstance(value, (str, bytes, bytearray)):
            if value in self.__requests:
                # Передано допустимое имя запроса
                super(self.__class__, self.__class__).request.fset(
                    self, self.__requests[value])
                # Определяем шаблон для проверки ответа
                self.__template = self.__templates[value]
                return None
            else:
                # Прередан запрос в виде строки
                # или недопустимое имя запроса
                try:
                    value = json.loads(value)
                except ValueError:
                    # Ошибка в формате запроса,
                    # или недопустимое имя запроса
                    raise ValueError(
                        "request = '{request}' request not supported"
                        " by this miner".format(request=value)) from None

        if value in self.__requests.values():
            # Передан допустимый запрос
            super(self.__class__, self.__class__).request.fset(self, value)
            # Получаем имя запроса
            value = next(
                (name for name, request in self.__requests.items()
                 if request == value),
            )
            # Определяем шаблон для проверки ответа
            self.__template = self.__templates[value]
        else:
            raise ValueError(
                "request = '{request}' request not supported"
                " by this miner".format(request=value))

    @property
    def response(self):
        """Ответ от сервера в формате dict,
        только статистика работы майнера
        """
        def listToDict(keys, values):
            """Создает словарь на основе списков
            с ключами и соответствующими значениями
            """
            return {key: value for key, value in zip(keys, values)}

        def strToInt(values):
            """Ищет в списках строки с данными и
            пытается преобразовать их к целочисленному типу
            """
            if isinstance(values, list):
                return [strToInt(value) for value in values]
            return int(values) if values.isdigit() else values

        value = super().response
        if self.error or value is None:
            return value

        # Ответ от сервера, только статистика работы майнера
        value = value['result']

        """Ответ от сервера приходит в виде словаря где данные
        - строки со значениями, разделенные ';', ':', '-'
        """

        # Преобразуем строки значений с разделителями в списки
        value = [split(';|:| - ', item) for item in value]
        # Ищем в списках данные и пытаемся
        # преобразовать их к целочисленному типу
        value = strToInt(value)

        # Шаблон создаваемого словаря
        keys = {
            'Version': ['Number', 'Type'],
            'Uptime': None,
            'ETH': ['Hashrate', 'Shares', 'Rejected'],
            'ETH Detailed': None,
            'DCR': ['Hashrate', 'Shares', 'Rejected'],
            'DCR Detailed': None,
            'GPU': ['Temperatures', 'Fan Speeds'],
            'Pools': ['Host', 'Port'],
            'Details': [
                'ETH Invalid Shares',
                'ETH Pool Switches',
                'DCR Invalid Shares',
                'DCR Pool Switches',
            ],
        }

        # Создаем словарь
        value = listToDict(keys, value)

        # Создаем вложенные словари
        for key in ['Version', 'ETH', 'DCR', 'Details']:
            value[key] = listToDict(keys[key], value[key])

        # Время работы майнера (список из одного
        # значения преобразуем просто в значение)
        value['Uptime'] = value['Uptime'][0]
        # Параметы GPU, разделяем температуры
        # и скорости вращения вентиляторов на два списка
        value['GPU'] = listToDict(
            keys['GPU'],
            [value['GPU'][::2], value['GPU'][1::2]]
        )
        # Прводим к требуемому представлению информацию по pool'ам
        value['Pools'] = [
            listToDict(keys['Pools'], item)
            for item in zip(*[iter(value['Pools'])] * 2)
        ]
        return value

    @response.setter
    def response(self, value):
        """Ответ от сервера должен соответсвовать API"""
        # Если ответа не ожидается
        if not self.__template:
            super(self.__class__, self.__class__).response.fset(self, None)
            return None

        try:
            # В ответе присутствуют все поля и их тип соответствует
            validate(
                json.loads(value),
                self.__template,
                disallow_unknown_properties=True,
            )
        except ValueError as e:
            self.errorResponse(e, value)
            return None

        super(self.__class__, self.__class__).response.fset(self, value)
        return None
