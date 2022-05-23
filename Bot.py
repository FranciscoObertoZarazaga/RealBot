from Config import THREADS
from Strategy import *
import Tester
import Telegram
from time import sleep
from Trading import *
from Symbol import *


class Bot:
    def __init__(self):
        self.kl = Klines()
        self.on = True
        self.data = self.get_data()
        self.last_status = get_status()
        self.best_price = 0
        self.buy_price = 0

    # Main
    def run(self):
        while self.on:
            try:
                self.data = self.get_data()
                price = self.get_price()
                action = self.analyze()
                do(action)
                status = get_status()
                self.change(status)
                if status:
                    self.buy_price = verify_price(self.best_price)
                    self.best_price = verify_price(self.best_price)
                    if price > self.best_price:
                        self.best_price = price
                        if price > self.buy_price * 1.012:
                            all_set_stop_loss(price)

                Tester.TESTER.set_last_activity()
                self.last_status = status
                sleep(3)
            except Exception as e:
                Telegram.TELEGRAM.notify(e)
                self.stop()

    def analyze(self):
        return good_buy_moment(self.data)

    @staticmethod
    def do(action):
        if action == 1 and not get_status():
            all_buy()

    @staticmethod
    def notify(status):
        if status is True:
            Telegram.TELEGRAM.notify(f'[{CONFIG.get_symbol()}]\nEl bot ha identificado un BUEN momento en el mercado y ha decidido COMPRAR')
        else:
            Telegram.TELEGRAM.notify(f'[{CONFIG.get_symbol()}]\nEl bot ha identificado un MAL momento en el mercado y ha decidido VENDER')

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

    def get_data(self):
        self.kl.load()
        return self.kl.get_klines()

    def get_price(self):
        return self.data['Close'][-1]

    def change(self, status):
        if self.last_status is None:
            return False
        if self.has_changed(status):
            self.notify(status)
            if status:
                self.buy_price = self.get_price()
                self.best_price = self.buy_price

    def has_changed(self, status):
        return self.last_status != status


BOT = Bot()
