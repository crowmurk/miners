# -*- coding: utf-8 -*-

"""
Модуль для опроса майнеров.
    Позволяет отправлять запросы к майнерам в формате json.
        Подерживаются запросы к майнерам:
            'Claymore's Dual Ethereum AMD GPU Miner v 9.8'
            'Claymore's CryptoNote GPU Miner v9.7
            'EWBF's CUDA ZCash miner v 0.3.4b'
            'CGMiner v 4.9.0 on Antminer S9'"""

from .miner import Miner
from .zcash import ZCash
from .etherium import Etherium
from .monero import Monero
from .cgminer import CGMiner
from .sender import Sender

__all__ = ['Miner', 'ZCash', 'Etherium', 'Monero', 'CGMiner', 'Sender']

__version__ = "1.2.2"
__author__ = "varga"
