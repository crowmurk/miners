#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Модуль содержит реализацию класса Pool"""

import socket
import http.client
import json

class Pool():
    """Отправляет запросы к пулу"""
    def __init__(self, pool, port, timeout):
        """
            Аргументы:
                pool: адрес пула
                port: порт пула
                timeout: время ожидания ответа пула"""

        self.pool = pool
        self.port = port
        self.timeout = timeout

    @property
    def error(self):
        """Статус последнего запроса"""
        try:
            return self.__error
        except AttributeError:
            return True

    @error.setter
    def error(self, value):
        """Статус последнего запроса, должен быть True или False"""
        if isinstance(value, bool):
            self.__error = value
        else:
            raise ValueError("pool request status '{error}' must be boolean type".format(error=value))

    @property
    def pool(self):
        """Пул"""
        try:
            return self.__pool
        except AttributeError:
            return None

    @pool.setter
    def pool(self, value):
        """Адрес пула должен быть IP адресом или разрешенным DNS"""
        try:
            socket.gethostbyname(value)
            self.__pool = value
        except socket.error as e:
            self.errorResponse(e, value)

    @property
    def port(self):
        """Порт пула"""
        try:
            return self.__port
        except AttributeError:
            return None

    @port.setter
    def port(self, value):
        """Порт пула, должен находится в передлах от 1  до 65535 и быть целым числом"""
        if value in range(1, 65536):
            self.__port = value
        else:
            raise ValueError("pool port '{port}' must be in range 1..65535".format(port=value))

    @property
    def timeout(self):
        """Время ожидани ответа пула"""
        try:
            return self.__timeout
        except AttributeError:
            return None

    @timeout.setter
    def timeout(self, value):
        """Время ожидани ответа пула, должно быть в пределах от 1 до 60 и быть целым"""
        if value in range(1, 61):
            self.__timeout = value
        else:
            raise ValueError("pool response timeout '{timeout}' must be in range 1..60".format(timeout=value))

    @property
    def response(self):
        """Ответ от пула в формате dict"""
        try:
            if self.__response is None:
                return self.__response
            else:
                return json.loads(self.__response)
        except AttributeError:
            return None

    @response.setter
    def response(self, value):
        """Ответ от пула, должен быть в формате json"""
        try:
            if value is not None:
                json.loads(value)
            self.__response = value
            self.__error = False
        except ValueError as e:
            self.errorResponse(e, value)

    def errorResponse(self, error, value):
        """Если не получен ответ от пула или неверный формат ответа
           заменяет ответ сообщением об ошибке и устанавливает соответвующий флаг"""
        self.__error = True
        self.__response = json.dumps({"error_type": type(error).__name__,
                                      "error_data": str(value),
                                      "error_message:": str(error)})

    def sendRequest(self, url):
        """
            Отправляет запрос к пулу
               Возвращает:
                   True: получен ответ от пула
                   False: ошибка выполнения запроса, ответ не получен"""

        # Если не задан адрес пула
        if not self.pool:
            return False

        try:
            # Соединяемся и делаем запрос
            connection = http.client.HTTPSConnection(self.__pool, self.__port, timeout=self.__timeout)
            connection.request('GET', url)
            connection.sock.settimeout(self.__timeout)
            result = connection.getresponse()
            data = result.read()
        except (http.client.HTTPException, socket.error) as e:
            # Ели ошибка, запускаем обработчик и возвращаем соответсвующий статус
            try:
                self.errorResponse(e, '{}: {} '.format(result.status, result.reason))
            except NameError:
                self.errorResponse(e, None)
            return False
        finally:
            connection.close()

        # Сохранаяем запрос и возвращаем соответсвующий статус
        self.response = data
        return True
