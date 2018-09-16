# -*- coding: utf-8 -*-

"""Модуль содержит реализацию класса Sender"""

from copy import deepcopy
import queue as Queue
import threading

from validictory import validate

from .zcash import ZCash
from .etherium import Etherium
from .monero import Monero
from .cgminer import CGMiner


class Sender():
    """Опрашивает майнеры из переданного списка"""

    def __init__(self, miners):
        """Аргументы:
           miners: список для опроса майнеров в формате dict:
               {'id': {'Host': str, 'Port': int,
                       'Miner': str, 'Request': (str | list),
                       'Timeout': int, 'Description': str }, }
           где:
               id - netbios имя имя хоста или другой идентификатор
               Host - ip адрес хоста
               Port - порт майнера
               Miner - тип майнера
               Request - тип запроса
               Timeout - таймаут ожидания ответа от майнера
               Description - описание хоста (необязательное поле)
        """

        self.__supportedMiners = {
            'Etherium': Etherium,
            'ZCash': ZCash,
            'Monero': Monero,
            'CGMiner': CGMiner,
        }

        # Шаблон для проверки параметров опроса майнера
        self.__template = {
            "type": "object",
            "properties": {
                "Host": {"type": "string"},
                "Port": {"type": "integer"},
                "Miner": {"type": "string"},
                "Request": {
                    "type": [
                        "string",
                        {
                            "array": {"type": "string"},
                        },
                    ],
                },
                "Timeout": {"type": "integer"},
                "Description": {
                    "type": "string",
                    "required": False,
                    "blank": True
                },
            },
        }

        self.__results = {}
        self.miners = miners

    @property
    def supportedMiners(self):
        """Поддерживаемые майнеры"""
        return self.__supportedMiners.keys()

    @property
    def miners(self):
        """Список параметров опроса майненров в формате dict:

        [{'id': {'Host': str, 'Port': int,
                 'Miner': str, 'Request': (str | list),
                 'Timeout': int, 'Description': str, }, }, ]
        Поле 'Description' не обязательно
        """
        try:
            return deepcopy(self.__miners)
        except AttributeError:
            return None

    @miners.setter
    def miners(self, value):
        """Параметры опроса майненров в формате dict:

            [{'id': {'Host': str, 'Port': int,
                    'Miner': str, 'Request': (str | list),
                    'Timeout': int, 'Description': str }, }, ]
            Поле 'Description' не обязательно
        """

        # Если передан не словарь
        if not isinstance(value, dict):
            raise ValueError(
                "miners list must be dictionary"
            )

        # Проверяем настройки для каждого майнера на соответвие шаблону
        for item in value:
            try:
                validate(
                    value[item],
                    self.__template,
                    disallow_unknown_properties=True
                )
                # Если тип майнера не поддерживается
                if value[item]['Miner'] not in self.supportedMiners:
                    raise ValueError(
                        "miner = '{miner}' not supported".format(
                            miner=value[item]['Miner'],
                        ),
                    )
            except ValueError as e:
                raise ValueError(
                    "miner = '{miner}' error in miner"
                    " settings ({error})".format(
                        miner=item, error=e
                    )
                ) from None

        self.__miners = deepcopy(value)

        # Создаем список запросов к майнеру
        for item in value:
            if isinstance(value[item]['Request'], str):
                self.__miners[item]['Request'] = [
                    self.__miners[item]['Request'],
                ]

    @property
    def results(self):
        """Результаты опроса майнеров в формате dict"""
        try:
            return deepcopy(self.__results)
        except AttributeError:
            return None

    @property
    def union(self):
        """Результаты опроса майнеров, в формате dict
        с параметрами запросов и полученными ответами
        """
        union = self.results
        # Порядок ключей в возвращаемом словаре
        keys = ['Host', 'Port', 'Miner', 'Exchange', 'Description']
        # Объединяем словари с настройками запросов к майнерам и ответами
        for name in union:
            union[name].update(self.miners[name])
            union[name] = {
                key: union[name][key]
                for key in (
                    keys if 'Description' in self.miners[name] else keys[:-1]
                )
            }
        return union

    def sendRequests(self):
        """Опрашивает майнеры"""

        def sendOne():
            """Выполняет запросы к майнерам из очереди"""
            # Берем из очереди экземпляр майнера и имя сервера
            name, miner = queue.get()
            # Делаем запрос
            miner.sendRequest()
            # Сохраняем результаты
            with lock:
                exchange = {
                    'Request': miner.request,
                    'Response': miner.response,
                    'Error': miner.error,
                }
                if name not in self.__results:
                    self.__results[name] = {}
                    self.__results[name]['Exchange'] = [exchange, ]
                else:
                    self.__results[name]['Exchange'].append(exchange)

            # Сообщаем о выполнении задания
            queue.task_done()

        # Очеред задания опроса майнеров
        queue = Queue.Queue()
        # Замок на добавление данных
        lock = threading.Lock()
        # Для к каждого майнера из списка
        for name, settings in self.miners.items():
            # Для каждого запроса
            for request in settings['Request']:
                miner = self.__supportedMiners[settings['Miner']](
                    settings['Host'],
                    settings['Port'],
                    request,
                    settings['Timeout']
                )
                # Добавляем задание в очередь
                queue.put((name, miner))
                # Создаем отдельную нить
                thread = threading.Thread(target=sendOne)
                thread.daemon = True
                thread.start()
        # Ожидаем выполнения всех заданий
        queue.join()
