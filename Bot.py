import random

from Klines import Klines
from Strategy import *
from Trader import TRADERS
from threading import Thread
from Tester import TESTER
from Telegram import TELEGRAM


class Bot:
    def __init__(self):
        super(Bot, self).__init__()
        self.kl = Klines()
        self.last_status = None

    def run(self):
        self.kl.load()
        kline = self.kl.getKlines()
        points = 0
        points += SqueezeStrategy(kline)
        status = self.get_last_trade()
        self.notify(status)
        if status and random.randint(0, 5) == 1:
            self.all_set_stop_loss()

        if points > 0:
            self.all_buy()
        if points < 0:
            self.all_sell()
        self.last_status = status
        TESTER.set_last_activity()

    def update(self, _):
        self.run()

    def all_buy(self):
        buy_threads = list()
        for trader in TRADERS:
            buy_threads.append(Thread(target=trader.buy))
        for thread in buy_threads:
            thread.start()

    def all_sell(self):
        sell_threads = list()
        for trader in TRADERS:
            sell_threads.append(Thread(target=trader.sell()))
        for thread in sell_threads:
            thread.start()

    def all_set_stop_loss(self):
        sell_threads = list()
        for trader in TRADERS:
            sell_threads.append(Thread(target=trader.set_stop_loss()))
        for thread in sell_threads:
            thread.start()

    def notify(self, status):
        if self.last_status is None:
            return 0
        if self.last_status != status:
            if status is True:
                TELEGRAM.notify('El bot ha identificado un BUEN momento en el mercado y ha decidido COMPRAR')
            else:
                TELEGRAM.notify('El bot ha identificado un MAL momento en el mercado y ha decidido VENDER')

    def get_last_trade(self):
        return TRADERS[0].get_last_trade()['isBuyer']


BOT = Bot()
