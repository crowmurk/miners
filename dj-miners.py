#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Загрузка заданий из БД Django - OK
# Отправка запросов майнерам - OK
# Загрузка результатов в БД - OK
# TODO Отправка статистики Zabbix

import sys
import os
import django
import datetime
import logging
import json

from systemd import journal
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

        # Инициализация логирования
        if self.config.log == 'FI':
            self.log = self.config.log_file
        else:
            self.log = self.config.log

        # Получаем настроки опроса майнеров
        self.__server_tasks = ServerTask.objects.filter(enabled=True)
        if not self.__server_tasks:
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
        for task in self.__server_tasks:
            tasks[task.id] = {
                'Host': task.server.host,
                'Port': task.server.port,
                'Miner': miner_name_map[task.server.miner.name],
                'Timeout': task.timeout,
                'Request': [request.request for request in task.requests.all()]
            }
        return tasks

    @property
    def log(self):
        """log: логирование результатов работы"""
        try:
            return self.__logger
        except AttributeError:
            return None

    @log.setter
    def log(self, value):
        """log: логирование результатов работы
        """

        journalName = 'minigstatistic'

        timeformat = "%Y.%m.%d-%H:%M:%S"

        self.__logger = logging.getLogger(journalName)
        self.__logger.setLevel(logging.INFO)

        if value == 'NO':
            # Не вести лог
            handler = logging.NullHandler()
            formatter = logging.Formatter()
        elif value == 'SY':
            # Запись лога в системный журнал
            handler = journal.JournalHandler(SYSLOG_IDENTIFIER=journalName)
            formatter = logging.Formatter('%(levelname)s: %(message)s')
        elif value == 'ST':
            # Вывод лога в stdout
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '[%(asctime)s] %(name)s: %(levelname)s: %(message)s',
                timeformat,
            )
        else:
            # Запись лога в файл
            handler = logging.FileHandler(value)
            formatter = logging.Formatter(
                '[%(asctime)s] %(name)s: %(levelname)s: %(message)s',
                timeformat,
            )

        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        self.__logger.addHandler(handler)

    def save(self, data):
        """Добавляет записи в БД
        """
        # Добавляем записи в БД
        for server_task_id, server_task_data in data.items():
            # Готовим данные для добавения
            server_task = ServerTask.objects.get(id=server_task_id, enabled=True)
            cleaned_data = {
                'server': server_task.id,
                'status': all(
                    [not line['Error'] for line in server_task_data['Exchange']],
                ),
                'executed': datetime.datetime.now(),
                'result': json.dumps(
                    [{'request': line['Request'], 'response': line['Response']}
                     for line in server_task_data['Exchange']],
                ),
            }

            # Форма обеспечивает проверку данных
            form = ServerStatisticForm(cleaned_data)

            if form.is_valid():
                form.save()
                self.log.info(
                    "Сохранение в БД:  {data}".format(
                        data=form.instance,
                    ),
                )
            else:
                self.log.error(
                    "Ошибка записи  в БД: {data}"
                    " Причина: {error}".format(
                        data=form.instance,
                        error=(form.errors, ),
                    ),
                )

def main():
    # Загружаем задания из БД
    works = Worker(config='Develop')

    # Опрашиваем майнеры
    sender = Sender(works.tasks)
    sender.sendRequests()

    # Добавление результатов в БД
    works.save(sender.results)

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
    from task.models import Config, ServerTask
    from task.forms import ServerStatisticForm

    sys.exit(main())
