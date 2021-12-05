from Klines import Klines
from Strategy import *
from Trader import TRADERS
from datetime import datetime
from Observed import Observed
from threading import Thread

class Bot(Observed):
    def __init__(self):
        super(Bot, self).__init__()
        self.kl = Klines()

    def run(self):
        self.kl.load()
        kline = self.kl.getKlines()
        points = 0
        points += WinStrategy(kline)

        if points > 0:
            self.all_buy()
        if points < 0:
            self.all_sell()
        self.notify(datetime.now().strftime("%H:%M %d-%m-%Y"))

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


BOT = Bot()
