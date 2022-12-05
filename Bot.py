import Config
from Config import THREADS, IS_REAL_TRADER, SYMBOL
import Tester
import Telegram
from time import sleep
from Binance import BINANCE
from Trader import TRADER
from threading import Thread
from Klines import KLINE
from Strategy import idiot_strategy
from Wallet import WALLET


class Bot:
    def __init__(self):
        self.on = True
        self.last_status = TRADER.getStatus()
        self.best_price = 0
        self.worst_price = 0
        self.buy_price = 0

    # Main
    def run(self):
        while self.on:
            try:
                status = TRADER.getStatus()

                self.do(status)
                self.change(status)

                Tester.TESTER.set_last_activity()
                self.last_status = status
                sleep(1)
            except Exception as e:
                Telegram.TELEGRAM.notify(f'Ha ocurrido un error: \n{e}')
                self.stop()

    #Realiza una accion dependiendo del estado actual
    def do(self, status):
        kl = KLINE.get()
        bid, ask = BINANCE.get_book_price(SYMBOL)
        if not status:
            goBuy = idiot_strategy(kl, bid)
            if goBuy:
                TRADER.buy(bid)
        else:
            self.take_profit(ask)
            TRADER.update(ask)



    # Notifica las operaciones de compra y venta
    @staticmethod
    def notify(status):
        if status is True:
            Telegram.TELEGRAM.notify(f'[{SYMBOL}]\nEl bot ha identificado un BUEN momento en el mercado y ha decidido COMPRAR')
        else:
            Telegram.TELEGRAM.notify(f'[{SYMBOL}]\nEl bot ha identificado un MAL momento en el mercado y ha decidido VENDER')
            Telegram.TELEGRAM.notify(str(WALLET))

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
                self.buy_price = TRADER.get_buy_price() if IS_REAL_TRADER else WALLET.buyPrice
                self.best_price = self.buy_price

    # Retorna si el estado ha cambiado
    def has_changed(self, status):
        return self.last_status != status

    # Persigue el precio y toma ganancia
    def take_profit(self, price):
        self.buy_price = self.verify_price(self.buy_price)
        self.best_price = self.verify_price(self.best_price)
        if price > self.best_price:
            self.best_price = price
            if price > self.buy_price * 1.004:
                TRADER.set_stop_loss(price)

    '''# Coloca una orden limit de compra por debajo del precio actual
    @staticmethod
    def buy_cheap(status, price):
        if not status:
            TRADER.set_buy_order_limit(price)'''

    @staticmethod
    def assert_price(price):
        assert price > 0, f'(best_price or buy_price)=({price}) must be mayor than 0'

    def verify_price(self, price):
        try:
            self.assert_price(price)
            return price
        except AssertionError:
            return TRADER.get_buy_price() if IS_REAL_TRADER else WALLET.buyPrice


BOT = Bot()
