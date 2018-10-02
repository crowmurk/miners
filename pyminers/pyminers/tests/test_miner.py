#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import json

from pyminers.miner import Miner

class MinerInitTest(unittest.TestCase):
    """Тестирование инициализации класса Miner
    """

    def setUp(self):
        self.kwargs = {
            'host': '127.0.0.1',
            'port': 6666,
            'timeout': 10,
            'request': '{}',
        }

    def test_empty_init(self):
        """Инициализация без параметров
        """
        with self.assertRaises(TypeError):
            Miner()

    def test_init_args_valid(self):
        """Инициализация c допустимыми параметрами
        """
        miner = Miner(**self.kwargs)

        # Начальный флаг ошибки всегда False
        self.assertEqual(miner.error, False)

    def test_init_host_invalid(self):
        """Недопустимый адрес при инициализации
        """
        self.kwargs['host'] = '8.8.8.8'
        with self.assertRaises(ValueError):
            Miner(**self.kwargs)

    def test_init_port_invalid(self):
        """Недопустимый порт при инициализации
        """
        self.kwargs['port'] = 0
        with self.assertRaises(ValueError):
            Miner(**self.kwargs)

    def test_init_timeout_invalid(self):
        """Недопустимый таймаут при инициализации
        """
        self.kwargs['timeout'] = 0
        with self.assertRaises(ValueError):
            Miner(**self.kwargs)

    def test_init_request_invalid(self):
        """Недопустимый запрос при инициализации
        """
        self.kwargs['request'] = 'some: invalid request'
        with self.assertRaises(ValueError):
            Miner(**self.kwargs)


class MinerSetUpTest(unittest.TestCase):
    """Тестирование установки
    параметров класса Miner
    """

    def setUp(self):
        kwargs = {
            'host': '127.0.0.1',
            'port': 6666,
            'timeout': 10,
            'request': '{}',
        }
        self.miner = Miner(**kwargs)

    def test_error_flag_valid(self):
        """Допустимый флаг ошибки
        """
        self.miner.error = True
        self.assertEqual(self.miner.error, True)

    def test_error_flag_not_bool(self):
        """Флаг ошибки не типа bool
        """
        with self.assertRaises(ValueError):
            self.miner.error = 'True'

    def test_host_valid(self):
        """Допустимый адрес
        """
        self.miner.error = True
        self.miner.host = '127.0.0.1'
        self.assertEqual(self.miner.host, '127.0.0.1')

        # Флаг ошибки должен быть сброшен
        self.assertEqual(self.miner.error, False)

    def test_host_common_ip(self):
        """ Адрес - общественный ip
        """
        with self.assertRaises(ValueError):
            self.miner.host = '8.8.8.8'

    def test_host_dns(self):
        """Адрес - DNS имя
        """
        with self.assertRaises(ValueError):
            self.miner.host = 'google.com'

    def test_port_valid(self):
        """Допустимый порт
        """
        self.miner.error = True
        self.miner.port = 6666
        self.assertEqual(self.miner.port, 6666)

        # Флаг ошибки должен быть сброшен
        self.assertEqual(self.miner.error, False)

    def test_port_max(self):
        """Номер порта больше допустимого
        """
        with self.assertRaises(ValueError):
            self.miner.port = 65536

    def test_port_min(self):
        """Номер порта меньше допустимого
        """
        with self.assertRaises(ValueError):
            self.miner.port = 0

    def test_timeout_valid(self):
        """Допустимый таймаут
        """
        self.miner.error = True
        self.miner.timeout = 10
        self.assertEqual(self.miner.timeout, 10)

        # Флаг ошибки должен быть сброшен
        self.assertEqual(self.miner.error, False)

    def test_timeout_max(self):
        """Таймаут больше допустимого
        """
        with self.assertRaises(ValueError):
            self.miner.timeout = 61

    def test_timeout_min(self):
        """Таймаут меньше допустимого
        """
        with self.assertRaises(ValueError):
            self.miner.timeout = 0

    def test_request_valid(self):
        """Допустимый формат запроса
        """
        self.miner.error = True
        self.miner.request = '{"key": "value"}'
        self.assertDictEqual(
            self.miner.request,
            json.loads('{"key": "value"}'))

        # Флаг ошибки должен быть сброшен
        self.assertEqual(self.miner.error, False)

    def test_request_invalid(self):
        """Неверный формат запроса
        """
        with self.assertRaises(ValueError):
            self.miner.request = 'some: invalid request'

    def test_set_error_response_mehod(self):
        """Метод errorResponce устнавливает
        правильные значения атрибутов
        """
        self.miner.errorResponse(
            ValueError("invalid format"),
            "invalid value",
        )

        invalid_response = {
            'error_type': 'ValueError',
            'error_data': 'invalid value',
            'error_message': 'invalid format',
        }
        self.assertDictEqual(self.miner.response, invalid_response)
        self.assertEqual(self.miner.error, True)

    def test_response_valid(self):
        """Допустимый формат ответа
        """
        self.miner.error = True
        self.miner.response = '{"key": "value"}'
        self.assertDictEqual(
            self.miner.response,
            json.loads('{"key": "value"}'))

        # Флаг ошибки должен быть сброшен
        self.assertEqual(self.miner.error, False)

    def test_responce_invalid(self):
        """Неверный формат ответа
        """
        self.miner.response = 'some invalid response'

        invalid_miner_response = {
            'error_type': 'JSONDecodeError',
            'error_data': 'some invalid response',
            'error_message': 'Expecting value: line 1 column 1 (char 0)',
        }
        self.assertDictEqual(self.miner.response, invalid_miner_response)
        self.assertEqual(self.miner.error, True)


# TODO Протестироваеть метод sendRequest
class MinerSendRequestTest(unittest.TestCase):
    """Тестирование работы с socket
    """

    def setUp(self):
        kwargs = {
            'host': '127.0.0.1',
            'port': 6666,
            'timeout': 10,
            'request': '{"command": "get_status"}',
        }
        self.miner = Miner(**kwargs)

    def test_respomse_valid(self):
        pass

    def test_respomse_invalid(self):
        pass


if __name__ == '__main__':
    unittest.main()
