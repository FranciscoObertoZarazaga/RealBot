from Config import THREADS
from Strategy import *
import Tester
import Telegram
from time import sleep
from Trading import *
from Symbol import *
from Binance import BINANCE


class Bot:
    def __init__(self):
        self.on = True
        self.last_status = get_status()
        self.best_price = 0
        self.worst_price = 0
        self.buy_price = 0

    # Main
    def run(self):
        while self.on:
            try:
                bid, ask = BINANCE.get_book_price(CONFIG.get_symbol())
                status = get_status()
                self.buy_cheap(status, bid)
                self.take_profit(status, ask)
                self.change(status)

                Tester.TESTER.set_last_activity()
                self.last_status = status
                sleep(1)
            except Exception as e:
                Telegram.TELEGRAM.notify(e)
                self.stop()

    # Notifica las operaciones de compra y venta
    @staticmethod
    def notify(status):
        if status is True:
            Telegram.TELEGRAM.notify(f'[{CONFIG.get_symbol()}]\nEl bot ha identificado un BUEN momento en el mercado y ha decidido COMPRAR')
        else:
            Telegram.TELEGRAM.notify(f'[{CONFIG.get_symbol()}]\nEl bot ha identificado un MAL momento en el mercado y ha decidido VENDER')

    # Inicia el Bot
    def start(self):
        if not THREADS['bot'].is_alive():
            self.on = True
            THREADS.update({'bot': Thread(target=self.run, name='bot')})
            THREADS['bot'].start()

    # Detiene el Bot
    def stop(self):
        if THREADS['bot'].is_alive():
            self.on = False
            THREADS['bot'].join()

    # Reinicia el Bot
    def restart(self):
        self.stop()
        self.start()

    # Realiza cambio de estado
    def change(self, status):
        if self.last_status is None:
            return False
        if self.has_changed(status):
            self.notify(status)
            if status:
                '''self.buy_price = get_buy_price()
                self.best_price = self.buy_price'''#ATENCION! DESCOMENTAR
                self.buy_price, _ = BINANCE.get_book_price(CONFIG.get_symbol())
                self.best_price = self.buy_price

    # Retorna si el estado ha cambiado
    def has_changed(self, status):
        return self.last_status != status

    #Persigue el precio y toma ganancia
    def take_profit(self, status, price, coef=.95):
        if status:
            self.buy_price = verify_price(self.best_price)
            self.best_price = verify_price(self.best_price)
            if price > self.best_price:
                self.best_price = price
                if price > self.buy_price * coef:
                    all_set_stop_loss(price)

    # Coloca una orden limit de compra por debajo del precio actual
    def buy_cheap(self, status, price):
        if not status:
            all_set_buy_order_limit(price)


BOT = Bot()
