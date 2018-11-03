# -*- coding: utf-8 -*-

"""Модуль содержит реализацию класса ZCash"""

import json

from validictory import validate

from .miner import Miner


class ZCash(Miner):
    """Отправляет запросы к майнеру ZCash"""

    def __init__(self, host='127.0.0.1', port=42000,
                 request='Statistic', timeout=5):
        """Аргументы:
        host: адрес сервера
        port: порт майнера
        request: тип запроса
            Поддерживаемы запросы (Statistic, )
        timeout: время ожидани ответа сервера
        """

        # Поддерживаемые запросы
        self.__requests = {
            'Statistic':
            {
                "id": 0,
                "method": "getstat",
            },
        }

        # Поля ответа и их тип и размер
        self.__templates = {
            'Statistic': {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "method": {"type": "string"},
                    "error": {"type": "null"},
                    "start_time": {"format": "utc-millisec"},
                    "current_server": {"type": "string"},
                    "available_servers": {"type": "integer"},
                    "server_status": {"type": "integer"},
                    "result": {
                        "items": {
                            "type": "object",
                            "properties": {
                                "gpuid": {"type": "integer"},
                                "cudaid": {"type": "integer"},
                                "busid": {"type": "string"},
                                "name": {"type": "string"},
                                "gpu_status": {"type": "integer"},
                                "solver": {"type": "integer"},
                                "temperature": {"type": "integer"},
                                "gpu_power_usage": {"type": "integer"},
                                "speed_sps": {"type": "integer"},
                                "accepted_shares": {"type": "integer"},
                                "rejected_shares": {"type": "integer"},
                                "start_time": {"format": "utc-millisec"},
                            },
                        },
                        "minItems": 1,
                    },
                },
            },
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
                    self, bytes(
                        json.dumps(self.__requests[value]),
                        encoding='utf-8') + b'\n')
                # Определяем шаблон для проверки ответа
                self.__template = self.__templates[value]
                return None
            else:
                # Прередан запрос в виде строки
                # или недопустимое имя запроса

                # Запрос к майнеру должен заканчиваться '\n'
                end = '\n' if isinstance(value, str) else b'\n'
                if not value.endswith(end):
                    raise ValueError(
                        "request = '{request}' request not supported"
                        " by this miner".format(request=value)) from None

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
            super(self.__class__, self.__class__).request.fset(
                self, bytes(
                    json.dumps(value),
                    encoding='utf-8') + b'\n')
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
        value = super().response
        return value if self.error or value is None else value['result']

    @response.setter
    def response(self, value):
        """Ответ от сервера должен соответсвовать API"""
        # Если ответа не ожидается
        if not self.__template:
            super(self.__class__, self.__class__).response.fset(self, None)
            return None

        try:
            # В ответе присутствую все поля и их тип соответствует
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
