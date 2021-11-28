from Klines import Klines
from Strategy import *
from Trader import Trader
from datetime import datetime
from SaveResults import save
from Binance import Binance

class Bot:
    def __init__(self, asset, symbol, interval, is_real_trader):
        self.symbol = symbol
        self.kl = Klines(symbol, interval)
        self.trader = Trader(symbol,is_real_trader)
        self.binance = Binance()
        self.indoor = True if self.binance.getCrypto(asset) * self.binance.get_price(self.symbol)[0] > self.binance.getusdt() else None

    def run(self):
        self.kl.load()
        kline = self.kl.getKlines()
        points = 0
        points += WinStrategy(kline)
        indoor = self.indoor

        if points > 0 and not indoor:
            self.trader.buy()
            self.indoor = True
            print('Compra')
        elif points < 0 and indoor:
            self.trader.sell()
            self.indoor = False
            print('Vende')
        open('state', 'w').write(f'ACTIVO: {datetime.now().strftime("%H:%M %d-%m-%Y")}')

    def update(self, _):
        self.run()
