from Config import THREADS
from Strategy import *
import Tester
import Telegram
from time import sleep
from Trading import *
from Symbol import *
from Binance import BINANCE
from datetime import datetime


class Bot:
    def __init__(self):
        self.on = True
        self.last_status = get_status()
        self.C1 = 'USDT'
        self.C2 = 'ETH'
        self.S12 = f'{self.C2}{self.C1}'
        #self.P12 = None if not self.last_status else get_buy_price()
        self.P12, _ = BINANCE.get_book_price(self.S12)
        print('Inicio:', datetime.now())
        #self.triangle = self.get_triangle()
        self.triangle = ['WIN']

    # Main
    def run(self):
        while self.on:
            try:
                #Compra BTC
                #self.P12, _ = BINANCE.get_book_price(self.S12)
                status = get_status()
                '''if not status:
                    #self.P12, _ = BINANCE.get_book_price(self.S12)
                    self.buy(self.C1, self.C2)
                    self.P12 = get_buy_price()
                    self.change(status)'''

                #Busca triangulo
                C3 = self.search()

                #Arbitrar
                self.arbitrar(C3)

                Tester.TESTER.set_last_activity()
                self.last_status = status
                sleep(5)
            except Exception as e:
                Telegram.TELEGRAM.notify(e)
                self.stop()


    @staticmethod
    def buy(fiat, coin):
        all_buy(fiat, coin)

    @staticmethod
    def sell(fiat, coin):
        all_sell(fiat, coin)

    def search(self):
        for c3 in self.triangle:
            try:
                s13, s23 = f'{c3}{self.C1}', f'{c3}{self.C2}'

                assert BINANCE.are_enable((self.S12, s13, s23))
                orderbook = BINANCE.client.get_orderbook_tickers()
                symbols = [symbol for symbol in orderbook if symbol['symbol'] in (s13, s23)]
                p13 = float([symbol['bidPrice'] for symbol in symbols if symbol['symbol'] == s13][0])
                p23 = float([symbol['askPrice'] for symbol in symbols if symbol['symbol'] == s23][0])
                print('Tasa:', self.get_rate(p13, p23))
                assert self.evaluate(p13, p23)
                print('-' * 50)
                print('EXITO!')
                print('Fin:', datetime.now())
                print(f'Triangulo ({self.S12}, {s23}, {s13})')
                print('Tasa:', self.get_rate(p13, p23))
                print(f'Precios ({self.S12}, {s23}, {s13}):', self.P12, p23, p13)
                print(f'Precio de compra: {self.P12}, Precio actual: {BINANCE.get_book_price(self.S12)[0]}')
                print('-' * 50)
                return c3
            except Exception as e:
                continue


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

    def get_triangle(self):
        par1 = BINANCE.getAllCoinsWith(self.C1)
        par2 = BINANCE.getAllCoinsWith(self.C2)
        return [coin for coin in par1 if coin in par2]

    def evaluate(self, p13, p23):
        num, den = self.calculate(p13, p23)
        return num > den

    def get_rate(self, p13, p23):
        num, den = self.calculate(p13, p23)
        return num/den

    def calculate(self,  p13, p23, d=0.999):
        #return numerador, denominador
        return p13 * d**3, self.P12 * p23

    def arbitrar(self, C3):
        self.buy(self.C2, C3)
        self.sell(self.C1, C3)



BOT = Bot()
