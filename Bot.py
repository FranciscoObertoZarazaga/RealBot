from Config import THREADS
from Klines import Klines
from Strategy import *
from Trader import TRADERS
from threading import Thread
from Tester import TESTER
import Telegram


class Bot:
    def __init__(self):
        self.kl = Klines()
        self.on = True
        self.last_status = None

    def run(self):
        while self.on:
            try:
                action = self.analyze()
                self.do(action)
                status = self.get_status()
                self.notify(status)
                if status:
                    self.all_set_stop_loss()

                self.last_status = status
                TESTER.set_last_activity()
            except Exception as e:
                Telegram.TELEGRAM.notify(e)
                exit(-1)

    def analyze(self):
        self.kl.load()
        kline = self.kl.getKlines()
        return SqueezeStrategy(kline)

    def do(self, action):
        if action > 0:
            self.all_buy()
        if action < 0:
            self.all_sell()

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
                Telegram.TELEGRAM.notify('El bot ha identificado un BUEN momento en el mercado y ha decidido COMPRAR')
            else:
                Telegram.TELEGRAM.notify('El bot ha identificado un MAL momento en el mercado y ha decidido VENDER')

    def get_status(self):
        return TRADERS[0].get_last_trade()['isBuyer']

    def start(self):
        if not THREADS['bot'].is_alive():
            self.on = True
            THREADS.update({'bot': Thread(target=self.run, name='bot')})
            THREADS['bot'].start()

    def stop(self):
        if THREADS['bot'].is_alive():
            self.on = False
            THREADS['bot'].join()

    def restart(self):
        self.stop()
        self.start()


BOT = Bot()
