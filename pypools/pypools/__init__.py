# -*- coding: utf-8 -*-

"""
Модуль для опроса пулов.
    Позволяет отправлять запросы к пулам в формате json.
        Подерживаются запросы к пулам:
            'NanoPool - nanopool.org' - Etherium, Monero
            'FlyPool - flypool.org' - ZCash"""

from .pool import Pool
from .flypool import FlyPool
from .nanopool import NanoPool
from .sender import Sender


__all__ = ['Pool', 'FlyPool', 'NanoPool', 'Sender']

__version__ = "1.0.2"
__author__ = "varga"
