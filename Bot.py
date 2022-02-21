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
        self.last_status = None

    # Main
    def run(self):
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
                if self.last_status != status:
                    sleep(300)
                self.last_status = status
                sleep(5)
            except Exception as e:
                Telegram.TELEGRAM.notify(e)
                exit(-1)

    @staticmethod
    def analyze(df):
        return squeeze_buster_strategy(df)

    def notify(self, status):
        if self.last_status is None:
            return 0
        if self.last_status != status:
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


BOT = Bot()
