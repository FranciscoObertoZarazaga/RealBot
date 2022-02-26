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
        self.last_status = get_status()
        # New strategy
        self.rate = .01
        self.last_price = None
        self.buy_price = None
        self.sell_price = None

    # Main
    '''def run(self):
        while self.on:
            try:
                data = self.get_data()
                action = self.analyze(data)
                do(action)
                status = get_status()
                self.notify(status)
                if status:
                    pass#all_set_stop_loss()

                Tester.TESTER.set_last_activity()
                if self.last_status != status and self.last_status is not None:
                    sleep(300)
                self.last_status = status
                sleep(5)
            except Exception as e:
                Telegram.TELEGRAM.notify(e)
                exit(-1)'''

    def run(self):
        while self.on:
            try:
                data = self.get_data()
                status = get_status()
                price = self.get_price(data)
                self.change(status)
                action = dynamic_stop_loss(status, price, self.last_price)
                self.do(action, price, status)

                Tester.TESTER.set_last_activity()
                self.last_status = status
                sleep(5)
            except Exception as e:
                Telegram.TELEGRAM.notify(e)
                exit(-1)

    @staticmethod
    def analyze(df):
        return squeeze_buster_strategy(df)

    def do(self, action, price, status):
        if action == -1:
            self.last_price = price
            self.sell_price = price * (1 - self.rate)
            print('sellprice' , self.sell_price)
        if action == 1:
            self.last_price = price
            self.buy_price = price * (1 + self.rate)
            print('buyprice' , self.buy_price)
        if self.buy_price == None:
            return 0
        if price >= self.buy_price and not status:
            all_buy()
        if self.sell_price == None:
            return 0
        if price <= self.sell_price and status:
            all_sell()

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

    @staticmethod
    def get_price(data):
        return data['Close'][-1]

    def change(self, status):
        if self.last_status is None:
            return False
        if self.has_changed(status):
            self.last_price = None
            self.sell_price = None
            self.buy_price = None
            self.notify(status)

    def has_changed(self, status):
        return self.last_status != status


BOT = Bot()
