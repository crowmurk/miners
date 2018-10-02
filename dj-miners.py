#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Тест подкючения к БД Django

import sys
import os
import django


def main():
    config = Config.objects.all()
    for line in config:
        print(line)


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

    django.setup()

    # Здесь импортируем модули проекта
    from task.models import Config

    sys.exit(main())
