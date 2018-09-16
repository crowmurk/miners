# -*- coding: utf-8 -*-

"""Модуль содержит реализацию класса CGMiner"""

import json

from validictory import validate

from .miner import Miner


class CGMiner(Miner):
    """Отправляет запросы к майнеру CGMiner"""

    def __init__(self, host='127.0.0.1', port=4028,
                 request='Summary', timeout=5):
        """Аргументы:
        host: адрес сервера
        port: порт майнера
        request: тип запроса
            Поддерживаемы запросы (Summary, Stats)
        timeout: время ожидани ответа сервера
        """

        # Поддерживаемые запросы
        self.__requests = {
            'Summary': b'{"command": "summary"}',
            'Stats': b'{"command": "stats"}',
        }

        # Поля ответа и их тип и размер
        self.__templates = {
            item: {
                "type": "object",
                "properties": {
                    "STATUS": {
                        "type": "array",
                        "items": [
                            {
                                "type": "object",
                                "properties": {
                                    "STATUS": {
                                        "enum": ["W", "I", "S", "E", "F"]
                                    },
                                    "When": {"format": "utc-millisec"},
                                    "Code": {"type": "integer"},
                                    "Msg": {"type": "string"},
                                    "Description": {"type": "string"},
                                },
                            },
                        ],
                        "minItems": 1,
                        "maxItems": 1,
                    },
                    "id": {"type": "integer"},
                },
            }
            for item in self.__requests}

        self.__templates['Summary']['properties'].update(
            {
                "SUMMARY": {
                    "type": "array",
                    "items": [
                        {
                            "type": "object",
                            "properties": {
                                "Elapsed": {"type": "integer"},
                                "GHS 5s": {"type": "string"},
                                "GHS av": {"type": "number"},
                                "Found Blocks": {"type": "integer"},
                                "Getworks": {"type": "integer"},
                                "Accepted": {"type": "integer"},
                                "Rejected": {"type": "integer"},
                                "Hardware Errors": {"type": "integer"},
                                "Utility": {"type": "number"},
                                "Discarded": {"type": "integer"},
                                "Stale": {"type": "integer"},
                                "Get Failures": {"type": "integer"},
                                "Local Work": {"type": "integer"},
                                "Remote Failures": {"type": "integer"},
                                "Network Blocks": {"type": "integer"},
                                "Total MH": {"type": "number"},
                                "Work Utility": {"type": "number"},
                                "Difficulty Accepted": {"type": "number"},
                                "Difficulty Rejected": {"type": "number"},
                                "Difficulty Stale": {"type": "number"},
                                "Best Share": {"type": "integer"},
                                "Device Hardware%": {"type": "number"},
                                "Device Rejected%": {"type": "number"},
                                "Pool Rejected%": {"type": "number"},
                                "Pool Stale%": {"type": "number"},
                                "Last getwork": {"format": "utc-millisec"},
                            },
                        },
                    ],
                    "minItems": 1,
                    "maxItems": 1},
            },
        )

        self.__templates['Stats']['properties'].update(
            {
                "STATS": {
                    "type": "array",
                    "items": [
                        {
                            "type": "object",
                            "properties": {
                                "BMMiner": {"type": "string"},
                                "Miner": {"type": "string"},
                                "CompileTime": {"type": "string"},
                                "Type": {"type": "string"},
                                "STATS": {"type": "integer"},
                                "ID": {"type": "string"},
                                "Elapsed": {"type": "integer"},
                                "Calls": {"type": "integer"},
                                "Wait": {"type": "number"},
                                "Max": {"type": "number"},
                                "Min": {"type": "number"},
                                "GHS 5s": {"type": "string"},
                                "GHS av": {"type": "number"},
                                "miner_count": {"type": "integer"},
                                "frequency": {"type": "string"},
                                "fan_num": {"type": "integer"},
                                "temp_num": {"type": "integer"},
                                "total_rateideal": {"type": "number"},
                                "total_freqavg": {"type": "number"},
                                "total_acn": {"type": "integer"},
                                "total_rate": {"type": "number"},
                                "temp_max": {"type": "integer"},
                                "Device Hardware%": {"type": "number"},
                                "no_matching_work": {"type": "integer"},
                                "miner_version": {"type": "string"},
                                "miner_id": {"type": "string"},
                            },
                            "patternProperties": {
                                "^temp[0-9]+": {"type": "integer"},
                                "^temp[0-9]+_[0-9]+": {"type": "integer"},
                                "^freq_avg[0-9]+": {"type": "number"},
                                "^chain_rateideal[0-9]+": {"type": "number"},
                                "^chain_acn[0-9]+": {"type": "integer"},
                                "^chain_acs[0-9]+": {
                                    "type": "string",
                                    "blank": True,
                                },
                                "^chain_hw[0-9]+": {"type": "integer"},
                                "^chain_rate[0-9]+": {
                                    "type": "string",
                                    "blank": True,
                                },
                                "^chain_xtime[0-9]+": {
                                    "type": "string",
                                    "blank": True,
                                },
                                "^chain_offside_[0-9]+": {
                                    "type": "string",
                                    "blank": True,
                                },
                                "^chain_opencore_[0-9]+": {
                                    "type": "string",
                                    "blank": True,
                                },
                            },
                        },
                    ],
                    "minItems": 1,
                    "maxItems": 1,
                },
            },
        )

        self.host = host
        self.port = port
        self.timeout = timeout

        # Запрос к серверу, должен соответсвовать API
        if request in self.__requests:
            self.request = self.__requests[request]
            self.__template = self.__templates[request]
        else:
            raise ValueError(
                "request = '{request}' request not supported"
                "by this miner".format(request=request))

    @property
    def requests(self):
        """Поддерживаемые запросы"""
        return self.__requests.keys()

    @property
    def response(self):
        """Ответ от сервера в формате dict,
        только статистика работы майнера
        """
        value = super().response
        return value

    @response.setter
    def response(self, value):
        """Ответ от сервера должен соответсвовать API"""
        # Если ответа не ожидается
        if not self.__template:
            super(self.__class__, self.__class__).response.fset(self, None)
            return None

        # Ошибка в ответе (Antminer's bug)
        value = value.replace(b'}{', b',')

        try:
            # В ответе присутствую все поля и их тип соответствует
            validate(
                json.loads(value),
                self.__template,
                disallow_unknown_properties=False,
            )
        except ValueError as e:
            self.errorResponse(e, value)
            return None

        super(self.__class__, self.__class__).response.fset(self, value)
        return None
