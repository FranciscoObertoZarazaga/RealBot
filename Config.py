from binance.enums import *
from tools.singleton import singleton

@singleton
class Config:
    def __init__(self):
        self._ASSET = 'BTC'
        self._FIAT = 'USDT'
        self._SYMBOL = self._ASSET + self._FIAT

    def set_config(self, asset):
        self._ASSET = asset
        self._SYMBOL = self._ASSET + self._FIAT

    def get_asset(self):
        return self._ASSET

    def get_fiat(self):
        return self._FIAT

    def get_symbol(self):
        return self._SYMBOL


IS_REAL_TRADER = False
INTERVAL = KLINE_INTERVAL_1HOUR
THREADS = dict()
CONFIG = Config()
PUBLIC_KEY = 'vcMdCj0x8aBQDqfhdtvINsXVqfvDbNOtwVYQyTdJtzKEKUY1nO90WmHidBx9stBB'
SECRET_KEY = 'USuTMTotFMlRhiBWvjqfMrofvDVG0XtnuGeAdZnkLCV6WaEzwtN420VfjUrDwi4c'
TELEGRAM_ID = 1369437188

