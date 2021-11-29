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
        self.indoor = True if self.binance.getCrypto(ASSET) * self.binance.get_price(SYMBOL)[0] > self.binance.getusdt() else None

    def run(self):
        self.kl.load()
        kline = self.kl.getKlines()
        points = 0
        points += WinStrategy(kline)
        indoor = self.indoor

        if points > 0 and not indoor:
            self.trader.buy()
            self.indoor = True
            self.telegram.notify('El bot ha identificado un BUEN momento en el mercado y ha decidido COMPRAR')
        if points < 0 and indoor:
            self.trader.sell()
            self.indoor = False
            save(self.trader)
            self.telegram.notify('El bot ha identificado un MAL momento en el mercado y ha decidido VENDER')
        self.tester.setLastActivity(datetime.now().strftime("%H:%M %d-%m-%Y"))

    def update(self, _):
        self.run()
