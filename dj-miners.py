#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Загрузка заданий из БД Django - OK
# Отправка запросов майнерам - OK
# TODO Загрузка результатов в БД
# TODO Отправка статистики Zabbix

import sys
import os
import django

from collections import namedtuple

from pyminers import Sender


class Worker():
    def __init__(self, config='Default'):
        # Получаем общие настройки, как словарь
        self.__config = Config.objects.filter(
            name=config,
            enabled=True,
        ).values().first()
        if not self.__config:
            # Конфигурация должна существовать
            # и быть включена
            raise ValueError(
                "Конфигурация с именем \"{config}\""
                " не существует или выключена".format(
                    config=config,
                )
            )

        # Получаем настроки опроса майнеров
        self.__tasks = Server.objects.filter(enabled=True)
        if not self.tasks:
            raise ValueError(
                "Задания отсутсвуют, проверьте"
                " настройки опроса майнеров"
            )

    @property
    def config(self):
        """Настроки работы скрипта
        """
        try:
            properties = namedtuple(
                'config',
                [item.lower() for item in self.__config.keys()],
            )
            return properties(*self.__config.values())
        except AttributeError:
            return None

    @property
    def tasks(self):
        """Параметры опроса майнеров
        """
        tasks = {}

        # TODO Sender для проверки исползует
        # свои именования майнеров, надо привести
        # к одному стандарту
        miner_name_map = {
            "Antminer S9 CGMiner": "CGMiner",
            "Claymore's CryptoNote": "Monero",
            "Claymore's Dual Ethereum": "Etherium",
            "EWBF's CUDA ZCash": "ZCash",
        }

        # Формируем список заданий для Sender
        for task in self.__tasks:
            tasks[task.id] = {
                'Host': task.server.host,
                'Port': task.server.port,
                'Miner': miner_name_map[task.server.miner.name],
                'Timeout': task.timeout,
                'Request': [request.name for request in task.requests.all()]
            }
        return tasks

def main():
    # Загружаем задания из БД
    works = Worker(config='Develop')

    # Опрашиваем майнеры
    sender = Sender(works.tasks)

    sender.sendRequests()
    # TODO Добавить время выполнения запроса
    # в результатах Sender

    # TODO Добавление результатов в БД

    # TODO Проверка отправки Zabbix


if __name__ == '__main__':

    # Текущая директория
    PROJECT_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

    # Имя проекта django
    DJANGO_PROJECT_NAME = 'miningstatistic'

    # Если проект лежит рядом (или добавляем
    # абсолютный путь к файлам проекта)
    sys.path.append(os.path.join(PROJECT_DIR, DJANGO_PROJECT_NAME))

    # Добавляем в окружение переменную с настройками проекта
    # как правило 'projectname.settings'
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        DJANGO_PROJECT_NAME + ".settings",
    )

    # Настройка окружения
    django.setup()

    # Здесь импортируем модули проекта
    from task.models import Config, Server

    sys.exit(main())
