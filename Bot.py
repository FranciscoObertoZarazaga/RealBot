from Config import THREADS
from Klines import Klines
from Strategy import *
from Tester import TESTER
import Telegram
from time import sleep
from Trading import *


class Bot:
    def __init__(self):
        self.kl = Klines()
        self.on = True
        self.last_status = None

    # Main
    def run(self):
        while self.on:
            try:
                action = self.analyze()
                do(action)
                status = get_status()
                self.notify(status)
                if status:
                    all_set_stop_loss()

                self.last_status = status
                TESTER.set_last_activity()
                sleep(30)
            except Exception as e:
                Telegram.TELEGRAM.notify(e)
                exit(-1)

    def analyze(self):
        self.kl.load()
        kline = self.kl.getKlines()
        return SqueezeStrategy(kline)

    def notify(self, status):
        if self.last_status is None:
            return 0
        if self.last_status != status:
            if status is True:
                Telegram.TELEGRAM.notify('El bot ha identificado un BUEN momento en el mercado y ha decidido COMPRAR')
            else:
                Telegram.TELEGRAM.notify('El bot ha identificado un MAL momento en el mercado y ha decidido VENDER')

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
