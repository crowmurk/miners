import unittest
import json

from pyminers.etherium import Etherium

class EtheriumInitTest(unittest.TestCase):
    """Тестирование инициализации класса Etherium
    """

    def setUp(self):
        self.kwargs = {
            'host': '127.0.0.1',
            'port': 6666,
            'timeout': 10,
            'request': 'Statistic',
        }

    def test_init_args_valid(self):
        """Инициализация c допустимыми параметрами
        """
        miner = Etherium(**self.kwargs)

        # Начальный флаг ошибки всегда False
        self.assertEqual(miner.error, False)

    def test_init_request_invalid_name(self):
        """Недопустимый запрос при инициализации - имя
        """
        self.kwargs['request'] = 'SomeName'
        with self.assertRaises(ValueError):
            Etherium(**self.kwargs)

    def test_init_request_invalid_str(self):
        """Недопустимый запрос при инициализации - строка
        """
        self.kwargs['request'] = json.dumps(
            {
                "method": "miner_getstat1",
            },
        )
        with self.assertRaises(ValueError):
            Etherium(**self.kwargs)

    def test_init_request_invalid_dict(self):
        """Недопустимый запрос при инициализации - словарь
        """
        self.kwargs['request'] = {
            "method": "miner_getstat1",
        }
        with self.assertRaises(ValueError):
            Etherium(**self.kwargs)


class EtheriumSetUpTest(unittest.TestCase):
    """Тестирование установки
    параметров класса Etherium
    """

    def setUp(self):
        kwargs = {
            'host': '127.0.0.1',
            'port': 6666,
            'timeout': 10,
            'request': 'Statistic',
        }
        self.miner = Etherium(**kwargs)

    def test_request_valid_name(self):
        """Допустимый формат запроса в виде имени запроса
        """
        self.miner.error = True
        self.miner.request = 'Statistic'
        self.assertDictEqual(
            self.miner.request,
            {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "miner_getstat1",
            },
        )

        # Флаг ошибки должен быть сброшен
        self.assertEqual(self.miner.error, False)

    def test_request_valid_str(self):
        """Допустимый формат запроса в виде строки
        """
        self.miner.error = True
        self.miner.request = json.dumps(
            {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "miner_getstat1",
            },
        )
        self.assertDictEqual(
            self.miner.request,
            {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "miner_getstat1",
            },
        )

        # Флаг ошибки должен быть сброшен
        self.assertEqual(self.miner.error, False)

    def test_request_valid_dict(self):
        """Допустимый формат запроса в виде словаря
        """
        self.miner.error = True
        self.miner.request = {
            "id": 0,
            "jsonrpc": "2.0",
            "method": "miner_getstat1",
        }
        self.assertDictEqual(
            self.miner.request,
            {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "miner_getstat1",
            },
        )

        # Флаг ошибки должен быть сброшен
        self.assertEqual(self.miner.error, False)

    def test_request_invalid_name(self):
        """Неверный формат запроса, имя
        """
        with self.assertRaises(ValueError):
            self.miner.request = 'SomeName'

    def test_request_invalid_str(self):
        """Неверный формат запроса, строка
        """
        with self.assertRaises(ValueError):
            self.miner.request = json.dumps(
                {
                    "method": "miner_getstat1",
                },
            )

    def test_request_invalid_dict(self):
        """Неверный формат запроса, словарь
        """
        with self.assertRaises(ValueError):
            self.miner.request = {
                "method": "miner_getstat1",
            }
