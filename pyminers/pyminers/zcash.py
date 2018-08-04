# -*- coding: utf-8 -*-

"""
Модуль содержит реализацию класса ZCash"""

import json
from validictory import validate
from .miner import Miner

class ZCash(Miner):
    """Отправляет запросы к майнеру ZCash"""
    def __init__(self, host='127.0.0.1', port=42000, request='Statistic', timeout=5):
        """
            Аргументы:
                host: адрес сервера
                port: порт майнера
                request: тип запроса
                    Поддерживаемы запросы (Statistic, )
                timeout: время ожидани ответа сервера"""
        # Поддерживаемые запросы
        self.__requests = {'Statistic': b'{"id":0, "method":"getstat"}\n', }

        # Поля ответа и их тип и размер
        self.__templates = {'Statistic':
                            {"type": "object",
                             "properties": {
                                 "id": {"type": "integer"},
                                 "method": {"type": "string"},
                                 "error": {"type": "null"},
                                 "start_time": {"format": "utc-millisec"},
                                 "current_server": {"type": "string"},
                                 "available_servers": {"type": "integer"},
                                 "server_status": {"type": "integer"},
                                 "result": {"items": {"type": "object",
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
                                                          "start_time": {"format": "utc-millisec"}}}, "minItems": 1}}}, }

        super().__init__(host, port, request, timeout)

    @property
    def requests(self):
        """Поддерживаемые запросы"""
        return self.__requests.keys()

    @property
    def request(self):
        """Запрос к серверу в формате dict"""
        return super().request

    @request.setter
    def request(self, value):
        """Запрос к серверу, должен соответсвовать API"""
        if value in self.__requests:
            super(self.__class__, self.__class__).request.__set__(self, self.__requests[value])
            self.__template = self.__templates[value]
        else:
            raise ValueError("request = '{request}' request not supported by this miner".format(request=value))

    @property
    def response(self):
        """Ответ от сервера в формате dict, только статистика работы майнера"""
        value = super().response
        return value if self.error or value is None else value['result']

    @response.setter
    def response(self, value):
        """Ответ от сервера должен соответсвовать API"""
        # Если ответа не ожидается
        if not self.__template:
            super(self.__class__, self.__class__).response.__set__(self, None)
            return None

        try:
            # В ответе присутствую все поля и их тип соответствует
            validate(json.loads(value), self.__template, disallow_unknown_properties=True)
        except ValueError as e:
            self.errorResponse(e, value)
            return None

        super(self.__class__, self.__class__).response.__set__(self, value)
        return None
