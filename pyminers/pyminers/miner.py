# -*- coding: utf-8 -*-

"""Модуль содержит реализацию класса Miner"""

import json
import socket
from ipaddress import ip_address


class Miner():
    """Отправляет запросы к майнеру в формате json"""

    def __init__(self, host, port, request, timeout):
        """Аргументы:
        host: адрес майнера
        port: порт майнера
        request: запрос в формате json
        timeout: время ожидани ответа майнера
        """

        self.host = host
        self.port = port
        self.timeout = timeout
        self.request = request

    @property
    def error(self):
        """Статус последнего запроса"""
        try:
            return self.__error
        except AttributeError:
            return True

    @error.setter
    def error(self, value):
        """Статус последнего запроса,
        должен быть True или False
        """
        if isinstance(value, bool):
            self.__error = value
        else:
            raise ValueError(
                "miner request status '{error}' "
                "must be boolean type".format(error=value),
            )

    @property
    def host(self):
        """Адрес майнера"""
        try:
            return self.__host
        except AttributeError:
            return None

    @host.setter
    def host(self, value):
        """Адрес майнера, должен быть из диапазона частных сетей"""
        try:
            address = ip_address(value)
        except ValueError as e:
            raise ValueError(
                "miner address {message}".format(message=e),
            ) from None

        if address.is_private:
            self.__host = value
            self.__error = False
        else:
            raise ValueError(
                "miner address '{address}' "
                "does not appear to be in "
                "private network".format(address=address),
            )

    @property
    def port(self):
        """Порт майнера"""
        try:
            return self.__port
        except AttributeError:
            return None

    @port.setter
    def port(self, value):
        """Порт майнера, должен находится в
        передлах от 1  до 65535 и быть целым числом
        """
        if value in range(1, 65536):
            self.__port = value
            self.__error = False
        else:
            raise ValueError(
                "miner port '{port}' must be "
                "in range 1..65535".format(port=value),
            )

    @property
    def timeout(self):
        """Время ожидани ответа майнера"""
        try:
            return self.__timeout
        except AttributeError:
            return None

    @timeout.setter
    def timeout(self, value):
        """Время ожидани ответа майнера, должно быть в
        пределах от 1 до 60 и быть целым
        """
        if value in range(1, 61):
            self.__timeout = value
            self.__error = False
        else:
            raise ValueError(
                "miner response timeout '{timeout}'"
                " must be in range 1..60".format(timeout=value),
            )

    @property
    def request(self):
        """Запрос к майнеру в формате dict"""
        try:
            return json.loads(self.__request)
        except AttributeError:
            return None

    @request.setter
    def request(self, value):
        """Запрос к майнеру, должен быть
        строкой в формате json
        """
        try:
            if isinstance(value, (str, bytes, bytearray)):
                json.loads(value)
                self.__request = value
            else:
                self.__request = bytes(
                    json.dumps(value),
                    encoding='utf-8',
                )
            self.__error = False
        except ValueError as e:
            raise ValueError(
                "miner request '{request}' {message} ".format(
                    request=value, message=e,
                ),
            ) from None

    @property
    def response(self):
        """Ответ от майнера в формате dict"""
        try:
            return json.loads(self.__response)
        except AttributeError:
            return None

    @response.setter
    def response(self, value):
        """Ответ от майнера, должен быть
        строкой в формате json
        """
        try:
            if isinstance(value, (str, bytes, bytearray)):
                json.loads(value)
                self.__response = value
            else:
                self.__response = bytes(
                    json.dumps(value),
                    encoding='utf-8',
                )
            self.__error = False
        except ValueError as e:
            self.errorResponse(e, value)

    def errorResponse(self, error, value):
        """Если не получен ответ от майнера или неверный
        формат ответа заменяет ответ сообщением об ошибке
        и устанавливает соответвующий флаг
        """
        self.__error = True
        self.__response = json.dumps(
            {
                "error_type": type(error).__name__,
                "error_data": str(value),
                "error_message": str(error),
            },
        )

    def sendRequest(self):
        """Отправляет запрос к майнеру в формате json

        return:
        True - получен ответ от майнера
        False - ошибка выполнения запроса, ответ не получен
        """
        if self.__error:
            return False

        received = b''
        bufferSize = 1024

        # Параметры подключения
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.__timeout)
        try:
            # Подключаемся, отправляем запрос
            sock.connect((self.__host, self.__port))
            sock.sendall(self.__request)
            # Получаем ответ
            buffer = sock.recv(bufferSize)
            while buffer:
                received += buffer
                buffer = sock.recv(bufferSize)
        except socket.error as e:
            # Ели ошибка, запускаем обработчик
            # и возвращаем соответсвующий статус
            self.errorResponse(e, None)
            return False
        finally:
            sock.close()
        # Сохранаяем запрос и возвращаем соответсвующий статус
        self.response = received.rstrip(b'\x00')
        return True
