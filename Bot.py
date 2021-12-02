from Klines import Klines
from Strategy import *
from Trader import Trader
from datetime import datetime
from SaveResults import save
from Binance import Binance
from Config import *

class Bot:
    def __init__(self,telegram, tester):
        self.kl = Klines(SYMBOL, INTERVAL)
        self.trader = Trader(SYMBOL,IS_REAL_TRADER)
        self.binance = Binance()
        self.telegram = telegram
        self.tester = tester

    def run(self):
        self.kl.load()
        kline = self.kl.getKlines()
        points = 0
        points += WinStrategy(kline)

        if points > 0:
            self.trader.buy()
            self.telegram.notify('El bot ha identificado un BUEN momento en el mercado y ha decidido COMPRAR')
        if points < 0:
            self.trader.sell()
            save(self.trader)
            self.telegram.notify('El bot ha identificado un MAL momento en el mercado y ha decidido VENDER')
        self.tester.setLastActivity(datetime.now().strftime("%H:%M %d-%m-%Y"))

    def update(self, _):
        self.run()
