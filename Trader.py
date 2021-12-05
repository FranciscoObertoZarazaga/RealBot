from Config import SYMBOL, IS_REAL_TRADER
from time import sleep
from DataBase import DATABASE
from Binance import Binance


class Trader:
    def __init__(self, id, name, api_key, secret_key):
        self.id = id
        self.name = name
        self.binance = Binance(api_key=api_key, secret_key=secret_key)

    def buy(self):
        if IS_REAL_TRADER:
            info = self.binance.buy(SYMBOL)

    def sell(self):
        if IS_REAL_TRADER:
            info = self.binance.sell(SYMBOL)

    def wait(self):
        sleep(10)


def get_all_traders():
    data = DATABASE.select('trader')
    traders = list()
    for trader in data:
        id = trader[0]
        name = trader[1].strip()
        api_key = trader[2].strip()
        secret_key = trader[3].strip()
        traders.append(Trader(id=id, name=name, api_key=api_key, secret_key=secret_key))
    return traders


TRADERS = get_all_traders()

















