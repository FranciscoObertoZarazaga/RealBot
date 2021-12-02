from Klines import Klines
from Strategy import *
from Trader import Trader
from datetime import datetime
from Binance import Binance
from Config import SYMBOL, INTERVAL, IS_REAL_TRADER
from Tester import TESTER

class Bot:
    def __init__(self):
        self.kl = Klines(SYMBOL, INTERVAL)
        self.trader = Trader(SYMBOL,IS_REAL_TRADER)
        self.binance = Binance()

    def run(self):
        self.kl.load()
        kline = self.kl.getKlines()
        points = 0
        points += WinStrategy(kline)

        if points > 0:
            self.trader.buy()
        if points < 0:
            self.trader.sell()
        TESTER.setLastActivity(datetime.now().strftime("%H:%M %d-%m-%Y"))

    def update(self, _):
        self.run()


BOT = Bot()
