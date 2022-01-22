from Klines import Klines
from Strategy import *
from Trader import TRADERS
from threading import Thread
from Tester import TESTER
from Telegram import TELEGRAM
from Binance import WS



class Bot:
    def __init__(self):
        super(Bot, self).__init__()
        self.kl = Klines()
        self.notified = {'buy': False, 'sell': False}

    def run(self):
        self.kl.load()
        kline = self.kl.getKlines()
        points = 0
        points += SqueezeStrategy(kline)

        if points > 0:
            self.all_buy()
        if points < 0:
            self.all_sell()
        TESTER.set_last_activity()

    def update(self, _):
        self.run()

    def all_buy(self):
        if not self.notified['buy']:
            self.notified = {'buy': True, 'sell': False}
            TELEGRAM.notify('El bot ha identificado un BUEN momento en el mercado y ha decidido COMPRAR')
            buy_threads = list()
            for trader in TRADERS:
                buy_threads.append(Thread(target=trader.buy))
            for thread in buy_threads:
                thread.start()
            WS.restart(1800)

    def all_sell(self):
        if not self.notified['sell']:
            self.notified = {'buy': False, 'sell': True}
            TELEGRAM.notify('El bot ha identificado un MAL momento en el mercado y ha decidido VENDER')
            sell_threads = list()
            for trader in TRADERS:
                sell_threads.append(Thread(target=trader.sell()))
            for thread in sell_threads:
                thread.start()
            WS.restart(1800)


BOT = Bot()
